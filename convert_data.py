import csv
import json
import re
import urllib.request
import io

def main():
    csv_file = 'data.csv'
    special_seats_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vS7o4i_KeQ4H_yxJ0_mx3gPo7ueIjihSscCxLJhe39BhBth4jx4zf5-SVsxEdNvmS8-zFhaaa66lAGE/pub?gid=1324007564&single=true&output=csv'
    
    special_seats_by_id = {}
    special_seats_by_name = {}
    db = {}

    try:
        # 1. Fetch Special Seats Data
        print(f"Fetching special seats data from {special_seats_url}...")
        with urllib.request.urlopen(special_seats_url) as response:
            content = response.read().decode('utf-8')
            f = io.StringIO(content)
            reader = csv.reader(f)
            next(reader) # Skip header
            for row in reader:
                if not row or len(row) < 6:
                    continue
                # TheaterID, TheaterName, ScreenID (Canonical), ScreenName, Row, SeatName, Note
                theater_id = row[0]
                screen_id_canonical = row[2]
                screen_name = row[3]
                
                seat_info = {
                    "row": row[4],
                    "name": row[5],
                    "note": row[6]
                }
                
                # Store by ID
                if screen_id_canonical not in special_seats_by_id:
                    special_seats_by_id[screen_id_canonical] = []
                special_seats_by_id[screen_id_canonical].append(seat_info)
                
                # Also store by TheaterID + Name as fallback
                name_key = f"{theater_id}_{screen_name}"
                if name_key not in special_seats_by_name:
                    special_seats_by_name[name_key] = []
                special_seats_by_name[name_key].append(seat_info)
        
        # 2. Process main data.csv
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Skip header
            
            for row in reader:
                if not row or len(row) < 5:
                    continue
                
                theater_id = row[2]
                theater_name = row[3]
                screen_id = row[4]
                screen_name = row[5]
                
                if theater_id not in db:
                    db[theater_id] = {
                        "name": theater_name,
                        "area": row[1],
                        "screens": {}
                    }
                
                # Safe access helper
                def get_col(idx):
                    return row[idx] if idx < len(row) else ""

                # Robust mapping: Try ID match first, then Name fallback
                special_seats = special_seats_by_id.get(screen_id, [])
                match_type = "ID"
                if not special_seats:
                    name_key = f"{theater_id}_{screen_name}"
                    special_seats = special_seats_by_name.get(name_key, [])

                screen_data = {
                    "name": screen_name,
                    "note": get_col(6),
                    "size": get_col(7),
                    "size_note": get_col(8),
                    "capacity": get_col(9),
                    "capacity_note": get_col(10),
                    "rec_row": get_col(11),
                    "rec_row_note": get_col(12),
                    "rec_num": get_col(13),
                    "rec_num_note": get_col(14),
                    "master_rec": get_col(15),
                    "master_rec_note": get_col(16),
                    "tags": [],
                    "special_seats": special_seats
                }
                
                # Add tags from notes or specs
                notes_text = (get_col(6) + " " + screen_name).lower()
                if "imax" in notes_text:
                    screen_data["tags"].append("IMAX")
                if "atmos" in notes_text:
                    screen_data["tags"].append("Dolby Atmos")
                if "screenx" in notes_text or "scren" in notes_text:
                    screen_data["tags"].append("ScreenX")
                if "tcx" in notes_text:
                    screen_data["tags"].append("TCX")
                if "4dx" in notes_text:
                    screen_data["tags"].append("4DX")
                if "轟音" in notes_text:
                    screen_data["tags"].append("轟音")
                if "bestia" in notes_text:
                    screen_data["tags"].append("BESTIA")
                     
                db[theater_id]["screens"][screen_id] = screen_data

        # Output as JS file
        with open('data.js', 'w', encoding='utf-8') as f:
            f.write('const CINEMA_DB = ')
            json.dump(db, f, indent=4, ensure_ascii=False)
            f.write(';')
            
        # Count total screens across all theaters
        total_screens = sum(len(theater["screens"]) for theater in db.values())
        print(f"Successfully converted {total_screens} screens to data.js")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
