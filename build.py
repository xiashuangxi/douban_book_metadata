import os
import shutil
import zipfile


def zip_dir(input_path, output_file):
    output_zip = zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED)
    for path, dir_names, file_names in os.walk(input_path):
        parsed_path = path.replace(input_path, '')
        for filename in file_names:
            full_path = os.path.join(path, filename)
            print('zip adding file %s' % full_path)
            output_zip.write(full_path, os.path.join(parsed_path, filename))
    output_zip.close()


if __name__ == "__main__":
    input_path = "src"
    out_path = "out"
    output_file = out_path + "/douban_book_metadata.zip"
    if os.path.exists(out_path):
        print('clean path %s' % out_path)
        shutil.rmtree(out_path)
    os.mkdir(out_path)
    zip_dir(input_path, output_file)
