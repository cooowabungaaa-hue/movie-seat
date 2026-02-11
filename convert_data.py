
import csv
import json
import re

def main():
    csv_file = 'data.csv'
    json_file = 'data.json'
    
    db = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Skip header
            
            # Column mapping based on the CSV structure
            # 0: Pref, 1: Area, 2: TheaterID, 3: TheaterName, 4: ScreenID, 5: ScreenName, 
            # 6: Note, 7: Size, 8: SizeNote, 9: Cap, 10: CapNote, 
            # 11: RecRow, 12: RecRowNote, 13: RecNum, 14: RecNumNote...
            
            seen_screens = set()
            
            for row in reader:
                if not row or len(row) < 5:
                    continue
                
                theater_id = row[2]
                theater_name = row[3]
                screen_id = row[4]
                screen_name = row[5]
                
                # Dedup based on ScreenID
                if screen_id in seen_screens:
                    continue
                seen_screens.add(screen_id)
                
                if theater_id not in db:
                    db[theater_id] = {
                        "name": theater_name,
                        "screens": {}
                    }
                
                # Safe access helper
                def get_col(idx):
                    return row[idx] if idx < len(row) else ""

                screen_data = {
                    "name": screen_name,
                    "note": get_col(6),
                    "size": get_col(7),
                    "capacity": get_col(9),
                    "rec_row": get_col(11),
                    "rec_num": get_col(13),
                    "tags": []
                }
                
                # Add tags from notes or specs
                if "IMAX" in screen_name or "IMAX" in get_col(6):
                    screen_data["tags"].append("IMAX")
                if "Atmos" in get_col(6):
                    screen_data["tags"].append("Dolby Atmos")
                if "SCREN" in get_col(6) or "ScreenX" in get_col(6): # Typo tolerant
                     screen_data["tags"].append("ScreenX")
                if "TCX" in get_col(6):
                     screen_data["tags"].append("TCX")
                     
                db[theater_id]["screens"][screen_id] = screen_data

        # Output as JS file
        with open('data.js', 'w', encoding='utf-8') as f:
            f.write('const CINEMA_DB = ')
            json.dump(db, f, indent=4, ensure_ascii=False)
            f.write(';')
            
        print(f"Successfully converted {len(seen_screens)} screens to data.js")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
