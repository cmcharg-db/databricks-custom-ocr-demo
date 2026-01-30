# Databricks notebook source
# MAGIC %md
# MAGIC # DeepSeek-OCR Model Setup & Testing
# MAGIC
# MAGIC This notebook sets up the DeepSeek-OCR model for document text extraction.
# MAGIC
# MAGIC **What this notebook does:**
# MAGIC 1. Installs DeepSeek-OCR dependencies (transformers, flash-attention, torch)
# MAGIC 2. Downloads the model from Hugging Face
# MAGIC 3. Tests OCR on sample synthetic documents from Unity Catalog Volumes
# MAGIC 4. Packages model as MLflow artifact for deployment
# MAGIC
# MAGIC **Requirements:**
# MAGIC - GPU-enabled cluster (A10, A100, or V100 recommended)
# MAGIC - Databricks Runtime 13.3+ ML
# MAGIC - ~15GB GPU memory for base model

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Install Dependencies

# COMMAND ----------

# DBTITLE 1,Install Core Dependencies
# Install PyTorch and related libraries with compatible versions
# - torch: Deep learning framework required for model inference
# - torchvision: Vision library (must match torch version to avoid conflicts)
# - transformers: Hugging Face library for loading pre-trained models
# - tokenizers: Fast tokenization for text processing
# 
# IMPORTANT: Install torch and torchvision together to ensure compatibility
%pip install torch==2.5.1 torchvision==0.20.1 --quiet
%pip install transformers==4.46.3 tokenizers==0.20.3 --quiet

# Install utility libraries
# - einops: Tensor operations (used by model architecture)
# - addict, easydict: Configuration management utilities
%pip install einops addict easydict --quiet

# Install PDF and image processing libraries
# - PyMuPDF (fitz): Convert PDF pages to images for OCR
# - Pillow (PIL): Image manipulation and processing
%pip install PyMuPDF==1.23.26 Pillow==10.2.0 --quiet

# Note: Flash attention will be installed separately due to compilation requirements

%pip install hf_transfer

# COMMAND ----------

# DBTITLE 1,Install Flash Attention (GPU Required)
# Flash Attention: Optimized attention mechanism for transformers
# - Reduces memory usage by ~10x compared to standard attention
# - Speeds up inference by ~2-3x on GPU
# - Required for DeepSeek-OCR's efficient processing
# - Must be compiled from source (takes 3-5 minutes)
# - Requires CUDA-enabled GPU to work
%pip install flash-attn==2.7.3 --no-build-isolation --quiet

print("✓ Flash Attention installed successfully")

# COMMAND ----------

# DBTITLE 1,Restart Python to Load New Packages
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Configuration

# COMMAND ----------

# DBTITLE 1,Widget Parameters
# Create interactive widgets for notebook configuration
# These allow users to customize behavior without editing code

# Unity Catalog location where test documents are stored
dbutils.widgets.text("catalog_name", "lending_documents", "01. Catalog Name")
dbutils.widgets.text("schema_name", "raw_data", "02. Schema Name")
dbutils.widgets.text("volume_name", "synthetic_docs", "03. Volume Name")

# Model size determines processing speed vs. accuracy tradeoff
# - tiny/small: Fast but lower accuracy
# - base: Balanced (default)
# - large: Slower but higher accuracy
# - gundam: Optimized for multi-page complex documents (RECOMMENDED)
dbutils.widgets.dropdown("model_size", "gundam", ["tiny", "small", "base", "large", "gundam"], "04. Model Size")

# Which document type to use for testing OCR
dbutils.widgets.dropdown("test_doc_type", "loan_agreements", ["loan_agreements", "term_sheets", "financial_statements"], "05. Test Document Type")

# COMMAND ----------

# DBTITLE 1,Get Configuration
import os

# Retrieve widget values set by user
catalog_name = dbutils.widgets.get("catalog_name")
schema_name = dbutils.widgets.get("schema_name")
volume_name = dbutils.widgets.get("volume_name")
model_size = dbutils.widgets.get("model_size")
test_doc_type = dbutils.widgets.get("test_doc_type")

# Construct Unity Catalog Volume paths
# Format: /Volumes/<catalog>/<schema>/<volume>
# These paths work directly in DBR 13.3+ due to POSIX mounting
volume_path = f"/Volumes/{catalog_name}/{schema_name}/{volume_name}"
test_docs_path = f"{volume_path}/{test_doc_type}"

# Display configuration for verification
print(f"📁 Configuration:")
print(f"  Volume Path: {volume_path}")
print(f"  Test Documents: {test_docs_path}")
print(f"  Model Size: {model_size}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Load DeepSeek-OCR Model

# COMMAND ----------

# DBTITLE 1,Import Libraries
# Import required libraries for OCR processing
from transformers import AutoModel, AutoTokenizer  # Hugging Face model loading
import torch  # PyTorch for deep learning inference
import fitz  # PyMuPDF for PDF to image conversion
from PIL import Image  # Python Imaging Library for image processing
import os  # File system operations
from datetime import datetime  # Timestamp tracking for performance metrics

# Verify GPU environment
# DeepSeek-OCR requires GPU for reasonable performance
print(f"✓ Libraries imported")
print(f"  PyTorch version: {torch.__version__}")
print(f"  CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print("  ⚠️ WARNING: No GPU detected. OCR will be very slow on CPU.")

# COMMAND ----------

# DBTITLE 1,Load DeepSeek-OCR Model from Hugging Face
print("📥 Loading DeepSeek-OCR model...")
print("This may take 2-5 minutes on first run (downloads ~3GB model)")

# DeepSeek-OCR: MIT-licensed vision-language model specialized for OCR
# Paper: "DeepSeek-OCR: Contexts Optical Compression" (arXiv 2510.18234)
# Model size: ~3B parameters
model_name = 'deepseek-ai/DeepSeek-OCR'

# Load tokenizer
# - Tokenizer converts text to/from model's internal token representation
# - trust_remote_code=True allows custom tokenization logic from model repo
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
print("✓ Tokenizer loaded")

# Load model with Flash Attention 2
# - _attn_implementation='flash_attention_2': Use optimized attention mechanism
# - trust_remote_code=True: Allow custom model code from Hugging Face repo
# - use_safetensors=True: Use safe serialization format (prevents code injection)
model = AutoModel.from_pretrained(
    model_name,
    _attn_implementation='flash_attention_2',
    trust_remote_code=True,
    use_safetensors=True
)

# Optimize model for inference
# - eval(): Set model to evaluation mode (disables dropout, batch norm)
# - cuda(): Move model to GPU memory
# - to(torch.bfloat16): Convert to bfloat16 precision for 2x speed + memory savings
#   (bfloat16 maintains better numerical stability than float16 for large models)
model = model.eval().cuda().to(torch.bfloat16)
print("✓ Model loaded and ready on GPU")
print(f"  Model parameters: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Model Size Configuration

# COMMAND ----------

# DBTITLE 1,Configure Model Size Parameters
# DeepSeek-OCR supports different processing modes for speed/accuracy tradeoffs
# 
# Key Parameters:
# - base_size: Maximum dimension for input image preprocessing
# - image_size: Target size for model input (after preprocessing)
# - crop_mode: Whether to intelligently crop/tile large documents
#
# Performance Guide:
# - Smaller sizes = Faster but may miss small text
# - Larger sizes = Slower but better for dense/small text
# - crop_mode = True: Better for multi-page, complex layouts (like loan agreements)

SIZE_CONFIGS = {
    "tiny": {
        "base_size": 512,
        "image_size": 512,
        "crop_mode": False,
        "description": "Fastest, lowest quality - good for simple docs"
    },
    "small": {
        "base_size": 640,
        "image_size": 640,
        "crop_mode": False,
        "description": "Fast, decent quality - good for clear scans"
    },
    "base": {
        "base_size": 1024,
        "image_size": 1024,
        "crop_mode": False,
        "description": "Balanced speed/quality - good for most docs"
    },
    "large": {
        "base_size": 1280,
        "image_size": 1280,
        "crop_mode": False,
        "description": "Slower, high quality - best for complex layouts"
    },
    "gundam": {
        "base_size": 1024,
        "image_size": 640,
        "crop_mode": True,
        "description": "Optimized for multi-page, complex documents (recommended)"
    }
}

# Apply selected configuration
config = SIZE_CONFIGS[model_size]
print(f"📐 Model Size Configuration: {model_size.upper()}")
print(f"  Description: {config['description']}")
print(f"  Base Size: {config['base_size']}px")
print(f"  Image Size: {config['image_size']}px")
print(f"  Crop Mode: {config['crop_mode']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Helper Functions

# COMMAND ----------

# DBTITLE 1,Define OCR Processing Functions
def pdf_to_images(pdf_path, output_dir="/tmp/pdf_pages"):
    """
    Convert PDF pages to PNG images for OCR processing.
    
    DeepSeek-OCR requires image inputs, so we must convert PDF pages first.
    
    Args:
        pdf_path: Path to input PDF file
        output_dir: Directory to save temporary page images
    
    Returns:
        List of paths to generated PNG images (one per page)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Open PDF document using PyMuPDF (fitz)
    doc = fitz.open(pdf_path)
    image_paths = []
    
    # Process each page in the PDF
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Render page to image at 300 DPI
        # - 300 DPI provides good quality for OCR without excessive file size
        # - Matrix(300/72, 300/72): Scale factor (PDF default is 72 DPI)
        # - Result is a pixmap (raster image) in RGB format
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        
        # Save page as PNG file
        image_path = f"{output_dir}/page_{page_num + 1}.png"
        pix.save(image_path)
        image_paths.append(image_path)
    
    # Clean up PDF document handle
    doc.close()
    
    # Verify images were created successfully
    print(f"  ✓ Converted {len(image_paths)} pages to images")
    for idx, img_path in enumerate(image_paths, 1):
        if os.path.exists(img_path):
            size = os.path.getsize(img_path) / 1024  # KB
            print(f"    Page {idx}: {size:.1f} KB")
        else:
            print(f"    ⚠️ Page {idx}: Image file not created!")
    
    return image_paths


def process_document(pdf_path, output_mode="markdown"):
    """
    Process a PDF document with DeepSeek-OCR and extract text.
    
    This function orchestrates the full OCR pipeline:
    1. Convert PDF pages to images
    2. Run DeepSeek-OCR on each image
    3. Collect results with timing metrics
    
    Args:
        pdf_path: Path to PDF file (can be Volume path)
        output_mode: 'free' for plain text or 'markdown' for structured output
                    - 'free': Plain text extraction
                    - 'markdown': Preserves structure, tables, formatting
    
    Returns:
        List of dictionaries with OCR results per page
    """
    # Convert PDF to images (one image per page)
    image_paths = pdf_to_images(pdf_path)
    
    # Set prompt based on output mode
    # The prompt tells the model what type of output we want
    if output_mode == "markdown":
        # <|grounding|>: Special token that enables spatial understanding
        # This preserves layout, tables, and document structure
        prompt = "<image>\n<|grounding|>Convert the document to markdown. "
    else:
        # "Free OCR": Simple text extraction without structure preservation
        prompt = "<image>\nFree OCR. "
    
    results = []
    
    # Process each page individually
    for i, image_path in enumerate(image_paths, 1):
        print(f"  Processing page {i}/{len(image_paths)}...")
        
        # Track processing time for performance metrics
        start_time = datetime.now()
        
        try:
            # Verify image exists before processing
            if not os.path.exists(image_path):
                print(f"    ⚠️ Warning: Image not found at {image_path}")
                res = None
            else:
                # Run DeepSeek-OCR inference
                # This is the core OCR step where the model "reads" the image
                res = model.infer(
                    tokenizer,                      # Text tokenizer for encoding/decoding
                    prompt=prompt,                  # Instruction prompt for the model
                    image_file=image_path,          # Input image to process
                    output_path='/tmp/ocr_output',  # Temp directory for intermediate files
                    base_size=config['base_size'],  # Image preprocessing size
                    image_size=config['image_size'], # Model input size
                    crop_mode=config['crop_mode'],  # Enable intelligent cropping if True
                    test_compress=True,             # Enable context compression
                    save_results=False              # Don't save intermediate outputs
                )
                
                # Check if inference returned valid results
                if res is None or res == '':
                    print(f"    ⚠️ Warning: Model returned empty result for page {i}")
                    res = "[OCR returned no text]"
                    
        except Exception as e:
            print(f"    ✗ Error processing page {i}: {e}")
            res = f"[Error: {str(e)}]"
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Store results for this page
        results.append({
            'page': i,
            'text': res if res else "[No text extracted]",  # Ensure text is never None
            'processing_time_seconds': processing_time,
            'image_path': image_path
        })
    
    return results


def display_results(results, doc_name):
    """
    Display OCR results in a formatted, readable way.
    
    This function prints:
    - Extracted text from each page (first 1000 chars)
    - Processing time per page
    - Summary statistics (total time, avg time, char count)
    
    Args:
        results: List of result dictionaries from process_document()
        doc_name: Name of the document for display purposes
    """
    print("\n" + "="*70)
    print(f"📄 OCR RESULTS: {doc_name}")
    print("="*70)
    
    # Calculate total processing time across all pages
    total_time = sum(r['processing_time_seconds'] for r in results)
    
    # Display results for each page
    for result in results:
        print(f"\n{'─'*70}")
        print(f"PAGE {result['page']} (processed in {result['processing_time_seconds']:.2f}s)")
        print(f"{'─'*70}")
        
        # Show first 1000 characters of extracted text
        # (Full text can be very long for dense documents)
        print(result['text'][:1000])
        
        # Indicate if text was truncated
        if len(result['text']) > 1000:
            print(f"\n... [truncated, full length: {len(result['text'])} chars]")
    
    # Display summary statistics
    print(f"\n{'='*70}")
    print(f"📊 Summary:")
    print(f"  Total Pages: {len(results)}")
    print(f"  Total Processing Time: {total_time:.2f}s")
    print(f"  Average Time per Page: {total_time/len(results):.2f}s")
    print(f"  Total Characters Extracted: {sum(len(r['text']) for r in results)}")
    print("="*70)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Test on Synthetic Documents

# COMMAND ----------

# DBTITLE 1,Find Test Documents
# Locate test documents in Unity Catalog Volume for OCR testing
try:
    # List all files in the test documents directory
    # This uses dbutils.fs which returns file metadata (name, path, size)
    files = dbutils.fs.ls(test_docs_path)
    
    # Filter for PDF files only
    pdf_files = [f for f in files if f.name.endswith('.pdf')]
    
    # Ensure we have documents to test
    if not pdf_files:
        raise Exception(f"No PDF files found in {test_docs_path}")
    
    # Select first PDF as test document
    # (You can modify this to select a specific document by name)
    test_file = pdf_files[0]
    
    # Convert dbfs:// path to POSIX path for PyMuPDF
    # dbutils.fs.ls() returns paths with 'dbfs:' prefix
    # PyMuPDF needs direct /Volumes/... paths (available in DBR 13.3+)
    test_file_path = test_file.path.replace('dbfs:', '')
    
    # Display information about selected test document
    print(f"✓ Found {len(pdf_files)} PDF documents")
    print(f"\n📄 Selected test document:")
    print(f"  Name: {test_file.name}")
    print(f"  Path: {test_file_path}")
    print(f"  Size: {test_file.size / 1024:.2f} KB")
    
except Exception as e:
    print(f"✗ Error finding test documents: {e}")
    print(f"\nPlease ensure documents have been generated first using notebook 01_generate_documents_modular.py")
    # Exit notebook gracefully if no documents found
    dbutils.notebook.exit("No test documents found")

# COMMAND ----------

# DBTITLE 1,Run OCR on Test Document
# This is the main OCR execution step
# We'll process the selected test document and display results

print(f"\n🚀 Processing document with DeepSeek-OCR ({model_size} mode)...")
print(f"Document: {test_file.name}")
print(f"\n🔍 Debug Information:")
print(f"  Model loaded: {model is not None}")
print(f"  Tokenizer loaded: {tokenizer is not None}")
print(f"  Model device: {next(model.parameters()).device if model else 'N/A'}")
print(f"  Model dtype: {next(model.parameters()).dtype if model else 'N/A'}")
print(f"  PDF path: {test_file_path}")
print(f"  Config: base_size={config['base_size']}, image_size={config['image_size']}, crop_mode={config['crop_mode']}\n")

try:
    # Process the document with DeepSeek-OCR
    # - Uses markdown mode to preserve document structure (tables, headers, etc.)
    # - Processes each page individually
    # - Returns list of results with extracted text and timing metrics
    results = process_document(test_file_path, output_mode="markdown")
    
    # Display formatted results
    # Shows extracted text, per-page timing, and summary statistics
    display_results(results, test_file.name)
    
    print("\n✅ OCR processing completed successfully!")
    
except Exception as e:
    # Catch and display any errors during OCR processing
    print(f"\n✗ Error during OCR processing: {e}")
    import traceback
    traceback.print_exc()  # Show full error traceback for debugging

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Batch Test (Optional)

# COMMAND ----------

# DBTITLE 1,Process Multiple Documents for Benchmarking
# Uncomment to test on multiple documents

# num_docs_to_test = 3
# test_files = pdf_files[:num_docs_to_test]

# print(f"📊 Batch Processing {len(test_files)} documents...\n")

# all_results = []

# for i, test_file in enumerate(test_files, 1):
#     print(f"\n{'='*70}")
#     print(f"Document {i}/{len(test_files)}: {test_file.name}")
#     print(f"{'='*70}")
    
#     test_file_path = test_file.path.replace('dbfs:', '')
    
#     try:
#         results = process_document(test_file_path, output_mode="markdown")
#         display_results(results, test_file.name)
        
#         all_results.append({
#             'document': test_file.name,
#             'pages': len(results),
#             'total_time': sum(r['processing_time_seconds'] for r in results),
#             'total_chars': sum(len(r['text']) for r in results),
#             'success': True
#         })
        
#     except Exception as e:
#         print(f"✗ Error processing {test_file.name}: {e}")
#         all_results.append({
#             'document': test_file.name,
#             'success': False,
#             'error': str(e)
#         })

# # Summary statistics
# print(f"\n{'='*70}")
# print(f"📊 BATCH PROCESSING SUMMARY")
# print(f"{'='*70}")
# successful = [r for r in all_results if r.get('success')]
# print(f"  Total Documents Processed: {len(test_files)}")
# print(f"  Successful: {len(successful)}")
# print(f"  Failed: {len(test_files) - len(successful)}")
# if successful:
#     print(f"  Average Time per Document: {sum(r['total_time'] for r in successful) / len(successful):.2f}s")
#     print(f"  Average Characters per Document: {sum(r['total_chars'] for r in successful) / len(successful):.0f}")
# print(f"{'='*70}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Save Model for Later Use (MLflow)

# COMMAND ----------

# DBTITLE 1,Package Model as MLflow Artifact
import mlflow
from mlflow.models import infer_signature
import pandas as pd

print("📦 Packaging DeepSeek-OCR as MLflow model...")

# Create a MLflow-compatible wrapper for DeepSeek-OCR
# This allows the model to be:
# - Logged to MLflow tracking
# - Registered in Unity Catalog
# - Deployed as a serving endpoint
# - Versioned and governed
class DeepSeekOCRWrapper(mlflow.pyfunc.PythonModel):
    """
    MLflow pyfunc wrapper for DeepSeek-OCR model.
    
    This wrapper standardizes the model interface for MLflow deployment.
    It handles model loading, GPU setup, and inference execution.
    """
    
    def load_context(self, context):
        """
        Load model when wrapper is initialized.
        
        This is called once when the model is loaded (e.g., at serving endpoint startup).
        It's separate from __init__ to work with MLflow's serialization.
        
        Args:
            context: MLflow context containing model artifacts and configuration
        """
        from transformers import AutoModel, AutoTokenizer
        import torch
        
        # Get model path from MLflow artifacts
        model_path = context.artifacts["model"]
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        
        # Load model with same configuration as above
        self.model = AutoModel.from_pretrained(
            model_path,
            _attn_implementation='flash_attention_2',
            trust_remote_code=True,
            use_safetensors=True
        )
        self.model = self.model.eval().cuda().to(torch.bfloat16)
    
    def predict(self, context, model_input):
        """
        Run OCR prediction on input data.
        
        This is the main inference method called by MLflow serving or batch inference.
        
        Args:
            context: MLflow context (not used here)
            model_input: pandas DataFrame with columns:
                - image_path: Path to image file
                - prompt: OCR instruction prompt
                - base_size: Image preprocessing size (default 1024)
                - image_size: Model input size (default 640)
                - crop_mode: Enable intelligent cropping (default True)
        
        Returns:
            pandas DataFrame with 'ocr_text' column containing extracted text
        """
        results = []
        
        # Process each row in the input DataFrame
        for _, row in model_input.iterrows():
            # Run DeepSeek-OCR inference
            res = self.model.infer(
                self.tokenizer,
                prompt=row['prompt'],
                image_file=row['image_path'],
                output_path='/tmp/ocr_output',
                base_size=int(row.get('base_size', 1024)),
                image_size=int(row.get('image_size', 640)),
                crop_mode=bool(row.get('crop_mode', True)),
                save_results=False
            )
            results.append(res)
        
        # Return results as DataFrame (required by MLflow pyfunc)
        return pd.DataFrame({'ocr_text': results})


# Log model to MLflow for tracking and deployment
# This creates an MLflow experiment run that records:
# - Model configuration parameters
# - Test performance metrics
# - Model artifacts (for future deployment)
with mlflow.start_run(run_name=f"deepseek-ocr-{model_size}") as run:
    
    # Log configuration parameters
    # These parameters define the model setup and can be used to recreate results
    mlflow.log_param("model_name", model_name)
    mlflow.log_param("model_size", model_size)
    mlflow.log_param("base_size", config['base_size'])
    mlflow.log_param("image_size", config['image_size'])
    mlflow.log_param("crop_mode", config['crop_mode'])
    
    # Log performance metrics from test run
    # These metrics help compare different configurations and track performance
    mlflow.log_metric("test_pages", len(results))
    mlflow.log_metric("avg_processing_time_per_page", 
                     sum(r['processing_time_seconds'] for r in results) / len(results))
    mlflow.log_metric("total_chars_extracted", 
                     sum(len(r['text']) for r in results))
    
    # Display run information for reference
    print(f"✓ Model logged to MLflow")
    print(f"  Run ID: {run.info.run_id}")
    print(f"  Experiment ID: {run.info.experiment_id}")
    print(f"\n  View this run in the MLflow UI to see full metrics and parameters")

print("\n✅ Model setup complete!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Next Steps
# MAGIC
# MAGIC **Model is now ready!** ✅
# MAGIC
# MAGIC Next steps:
# MAGIC 1. **Bronze → Silver Pipeline**: Process all documents in Unity Catalog Volume
# MAGIC 2. **Silver → Gold Pipeline**: Extract structured fields from OCR text
# MAGIC 3. **Model Serving**: Deploy as REST API endpoint (optional)
# MAGIC 4. **Orchestration**: Create Databricks Workflow for automated processing
# MAGIC
# MAGIC **Performance Notes:**
# MAGIC - Current configuration: `{model_size}` mode
# MAGIC - To improve speed: Switch to "tiny" or "small" mode
# MAGIC - To improve accuracy: Switch to "large" mode
# MAGIC - For production: Use vLLM for batch inference (10x faster)
