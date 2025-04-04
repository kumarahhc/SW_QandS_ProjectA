import csv
import json
"""This file is used to convert result Json files to csv"""
class FileManager:
    @staticmethod
    def JSON_Result_to_CSV(json_file_path, csv_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            header_written = False
            
            for entry in data:
                scenario_id = entry.get("Scenario ID", "")
                user_input = entry.get("User Input", "")
                
                # Extract JSON fields correctly
                json_data = entry.get("JSON", {})
                
                if isinstance(json_data, dict):  # Ensure it's a dictionary
                    row = {"Scenario ID": scenario_id, "User Input": user_input, **json_data}

                    if not header_written:
                        writer.writerow(row.keys())  # Write header
                        header_written = True

                    writer.writerow(row.values())  # Write values

        print(f"CSV file '{csv_file_path}' has been saved successfully.")
        
    def JSON_RAG_REsult_to_CSV(json_path, csv_path):# This is used to convert json file generated in RAG asisted analysis
        # Load JSON data from Disk path
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Writing JSON data to CSV
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        print(f"CSV file '{csv_path}' has been saved successfully.")

if __name__ == "__main__":
    #FileManager.JSON_Result_to_CSV("../data/test_results_01.json", "../data/test_results_01.csv")
    FileManager.JSON_RAG_REsult_to_CSV("../results/rag_test_result.json", "../results/rag_test_results.csv")
