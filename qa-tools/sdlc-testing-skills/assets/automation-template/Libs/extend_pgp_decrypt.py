import zipfile
import gnupg
import os
from robot.api.deco import keyword, library
from robot.api import logger

CRED_PATH = os.getenv("GOOGLESPACE")

@library
class ExtendPgpDecrypt:
    ROBOT_LIBRARY_SCOPE = "TEST CASE"
    
    def __init__(self):
        self.gpg = gnupg.GPG()
        

    @keyword("Decrypt PGP And Extract Zip")
    def decrypt_pgp_and_extract_zip(self, encrypted_file, output_dir, passphrase ='testpassword123' ):
        
        """
        Giải mã tệp PGP để có được tệp zip và trích xuất nội dung của tệp đó.
        Cài đặt thư viên `pip install python-gnupg -U`
        Args:
            encrypted_file (str): Đường dẫn đến tệp PGP đã mã hóa
            private_key_path (str): Đường dẫn đến tệp khóa riêng
            output_dir (str): Thư mục để lưu tệp zip đã giải mã và các tệp đã trích xuất
        
        Returns:
            list: danh sách: Danh sách các đường dẫn đến các tập tin được giải nén
        """
        file_name = os.path.splitext(os.path.basename(encrypted_file))[0]
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            zip_output = os.path.join(output_dir, f"{file_name}.zip")

            # Import private key
            # with open(os.path.join(CRED_PATH, 'private.key'), 'r') as key_file:
            with open(os.path.join('C:\\googlespace', 'private.key'), 'r') as key_file:
                key_data = key_file.read()
            import_result = self.gpg.import_keys(key_data)
            if import_result.count == 0:
                raise Exception("Failed to import private key")
            logger.info(f"Imported private key: {import_result.fingerprints}")

            # Decrypt PGP file


            with open(encrypted_file, 'rb') as f:
                decrypt_result = self.gpg.decrypt_file(
                    f,
                    passphrase=passphrase,
                    output=zip_output
                )
            if decrypt_result.ok:
                logger.info(f"Decrypted file saved to: {zip_output}")
                if decrypt_result.stderr:
                    logger.info(f"GPG warning: {decrypt_result.stderr}")
            else:
                raise Exception(f"Decryption failed: {decrypt_result.status} | stderr: {decrypt_result.stderr}")
            logger.info(f"Decrypted file saved to: {zip_output}")

            # Extract zip file
            extracted_files = []
            with zipfile.ZipFile(zip_output, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
                extracted_files = [os.path.join(output_dir, f) for f in zip_ref.namelist()]
            logger.info(f"Extracted files: {extracted_files}")

            return extracted_files

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise

# if __name__ == "__main__":
#     tt = PGPZipDecrypt()
#     file ='D:\\nexa_sftp\\VTCBVNVX_RECON01_STL20250604190000_20250604.pgp'
#     private_key_path = 'D:\\nexa\\pgp\\private.key'
#     passphrase = 'testpassword123'
#     output = 'D:\\nexa_sftp\\'
#     zip_file ='D:\\nexa_sftp\\decrypted.zip'
#     cc = tt.decrypt_pgp_and_extract_zip(file, private_key_path, output_dir=output)
#     print(cc)
#     # count = tt.count_files_in_zip(zip_file)
#     # print(count)
    