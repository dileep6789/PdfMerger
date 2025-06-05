import streamlit as st
import os
import tempfile
import zipfile
from io import BytesIO
from pypdf import PdfWriter

st.title("📂 PDF Merger: Match by Filename (Part A + Part B)")

# Upload files from each folder
part_a_files = st.file_uploader("📁 Upload all PDFs from Part A folder", type="pdf", accept_multiple_files=True)
part_b_files = st.file_uploader("📁 Upload all PDFs from Part B folder", type="pdf", accept_multiple_files=True)

if part_a_files and part_b_files:
    if st.button("🚀 Merge Matching PDFs"):
        with tempfile.TemporaryDirectory() as temp_dir:
            merged_dir = os.path.join(temp_dir, "merged")
            os.makedirs(merged_dir, exist_ok=True)

            # Convert uploads to dicts for filename matching
            files_a_dict = {file.name: file for file in part_a_files}
            files_b_dict = {file.name: file for file in part_b_files}

            all_names_a = set(files_a_dict.keys())
            all_names_b = set(files_b_dict.keys())

            common_files = all_names_a & all_names_b
            only_in_a = all_names_a - all_names_b
            only_in_b = all_names_b - all_names_a

            # Merge matching files
            for filename in common_files:
                file_a = files_a_dict[filename]
                file_b = files_b_dict[filename]

                merger = PdfWriter()

                a_path = os.path.join(temp_dir, f"a_{filename}")
                b_path = os.path.join(temp_dir, f"b_{filename}")
                merged_path = os.path.join(merged_dir, filename)

                with open(a_path, "wb") as f:
                    f.write(file_a.read())
                with open(b_path, "wb") as f:
                    f.write(file_b.read())

                merger.append(a_path)
                merger.append(b_path)
                merger.write(merged_path)
                merger.close()

                st.success(f"Merged: {filename}")

            # Report unmatched files
            for f in only_in_a:
                st.warning(f"⚠️ Skipped (found only in Part A): {f}")
            for f in only_in_b:
                st.warning(f"⚠️ Skipped (found only in Part B): {f}")

            # Create ZIP for download
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for fname in os.listdir(merged_dir):
                    fpath = os.path.join(merged_dir, fname)
                    zipf.write(fpath, arcname=fname)
            zip_buffer.seek(0)

            st.download_button(
                label="📦 Download Merged ZIP",
                data=zip_buffer,
                file_name="Merged_PDFs.zip",
                mime="application/zip"
            )
