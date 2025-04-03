import csv
import json

class FileManager:
    def JSON_Result_to_CSV(json_file_path, csv_file_path):
        def json_to_csv(json_file, csv_file):
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                header_written = False
                
                for entry in data:
                    scenario_id = entry["Scenario ID"]
                    user_input = entry["User Input"]
                    
                    for response in entry["AI Response"]:
                        row = {"Scenario ID": scenario_id, "User Input": user_input, **response}
                        
                        if not header_written:
                            writer.writerow(row.keys())
                            header_written = True
                        
                        writer.writerow(row.values())
            
            print(f"CSV file '{csv_file}' has been saved successfully.")
  

