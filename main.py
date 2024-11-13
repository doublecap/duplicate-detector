import os
import sys
import csv
from PIL import Image, ImageStat

# Initialize the list of duplicate file names
duplicates = []
processed_images = {}

def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()



# Returns a list of folders ready for processing
def find_folders_with_images(root_folder):
    folders_with_images = []
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"} # 13/11/2024 Currently other image types are not supported apart from .jpg 

    def is_folder_with_only_images(folder):
        has_files = False
        for entry in os.scandir(folder):
            if entry.is_file():
                has_files = True
                if os.path.splitext(entry.name)[1].lower() not in image_extensions:
                    return False  # Contains a non-image file
            elif entry.is_dir():
                if not is_folder_with_only_images(entry.path):
                    return False  # Contains a subfolder that isn't image-only
        return has_files  # Only image files if it has files

    def search_folder(folder):
        if is_folder_with_only_images(folder):
            folders_with_images.append(folder)
    
        for entry in os.scandir(folder):
            if entry.is_dir():
                search_folder(entry.path)  # Recursively search in subdirectory

    search_folder(root_folder)
    return folders_with_images



def find_duplicate_images(folder_path, output_csv):
    try:
        # Generate a list of image files by filtering for .jpg files
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]
        
        print("Searching folder: ", folder_path)
        # Loop through each image file
        for i, file1 in enumerate(image_files):
            progress_bar(i + 1, len(image_files), prefix='Progress:', suffix='Complete', length=50)
            file1_path = os.path.join(folder_path, file1)
            
            try:
                # Open the first image and calculate its mean pixel value
                with Image.open(file1_path) as img1:
                    stat1 = ImageStat.Stat(img1)
                    mean1 = stat1.mean  # Get the mean pixel values

                # Check if the mean pixel value already exists in processed images
                if tuple(mean1) in processed_images:
                    # If it exists, add both files and their paths to the duplicates list
                    duplicates.append((file1, file1_path, processed_images[tuple(mean1)][0], processed_images[tuple(mean1)][1]))
                else:
                    # Store the image mean in the processed dictionary with path information
                    processed_images[tuple(mean1)] = (file1, file1_path)
            except Exception as e:
                print(f"Error processing file {file1}: {e}")
                
        # Write duplicates to a CSV file
        with open(output_csv, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Duplicate Image", "Duplicate Path", "Original Image", "Original Path"])
            for dup in duplicates:
                writer.writerow(dup)
                
    except FileNotFoundError:
        print("The specified folder does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # Output the results
    if duplicates:
        print("Duplicate images found and recorded to CSV file.")
    else:
        print("No duplicate images found.")



def main(root_folder, output_csv):
    image_only_folders = find_folders_with_images(root_folder)
    
    for folder in image_only_folders:
        find_duplicate_images(folder, output_csv)



if __name__ == "__main__":

    # Specify the path to your image folder
    root_folder = "C:/Users/svpk9/Downloads/wetransfer_testiaineistoa_2024-11-03_1209/testiaineistoa/"
    output_csv = "C:/Users/svpk9/Downloads/wetransfer_testiaineistoa_2024-11-03_1209/testiaineistoa/duplicates.csv"

    # Call the function to find duplicate images
    main(root_folder, output_csv)