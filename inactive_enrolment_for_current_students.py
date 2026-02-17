import pandas as pd
import sys
import requests
import token_canvas
import os
from datetime import datetime, date, timezone


BASE_URL = "https://gmc.instructure.com"
ACCESS_TOKEN = token_canvas.TOKEN_KEY

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def get_active_enrolments(sis_user_id):
    enrolments = []
    url = f"{BASE_URL}/api/v1/users/sis_user_id:{sis_user_id}/enrollments"
    params = {
        "StudentEnrollment[]": ["active"],
        "per_page": 99999
    }

    while url:
        r = requests.get(url, headers=HEADERS, params=params)
        try :
            r.raise_for_status()
        except  Exception as e: 
            print(f"Error fetching enrolments for SIS User ID {sis_user_id}: {e}")
            # break   
            pass
        # r.raise_for_status()

        enrolments.extend(r.json())

        link_header = r.headers.get("Link", "")
        next_url = None

        if link_header:
            for part in link_header.split(","):
                if 'rel="next"' in part:
                    next_url = part.split(";")[0].strip()[1:-1]
                    break

        url = next_url
        params = None

    return enrolments


# -----------------------------
# READ CSV OR EXCEL
# -----------------------------
def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError("Unsupported file type")


if __name__ == "__main__":

    file_path = r"C:\Users\aphiwut.j\Documents\work\inactive accounts\suspension and cancellation emails in HubSpot\13-02-2026 suspension.xlsx"

    df = read_file(file_path)

    if "Student No" not in df.columns:
        raise ValueError("Column 'Student No' not found")

    now_local = str(datetime.now())
    print(type(now_local))

    # student_no_list = [ 
    #     114097,
    #     110575
    # ]
    # for student_no in student_no_list:
    for student_no in df["Student No"].dropna().astype(str):

        enrolments = get_active_enrolments(student_no)

        for i in enrolments:
            # if now_local[2:4] in str(i.get("sis_course_id", "")):
            #     print(now_local[2:4])
            #     print(student_no, i.get("sis_course_id"))
            #     print(i.get("id"))\
            try:
                # if i.get("sis_course_id").lower().startswith("g"):
                #     # print(student_no)
                #     # print(i.get("sis_course_id") , i.get("sis_course_id")[:3])
                #     # print(i.get("sis_course_id").split()[1][:2])
                #     # print(type(i.get("sis_course_id").split()[1][:2]))

                #     if i.get("sis_course_id").split()[1][:2] == now_local[2:4]:
                #         print(student_no)
                #         print(i.get("sis_course_id") , i.get("sis_course_id")[:2])
                #         print(type(i.get("sis_course_id")))

                #     # continue
                #     pass

                # if i.get("sis_course_id")[:2] == now_local[2:4]:
                if '26-T1' in str(i.get("sis_course_id")):
                    # Only process enrollments that are currently active
                    state = str(i.get("enrollment_state", "")).lower()
                    if state != "active":
                        print(f"Skipping enrollment {i.get('id')} for student {student_no} (state={state})")
                        continue

                    # Set this enrollment to inactive via Canvas API
                    student = student_no
                    sis_course = i.get("sis_course_id")
                    course_id = i.get("course_id")
                    enrollment_id = i.get("id")
                    print(f"Processing student {student}, sis_course_id={sis_course}, enrollment_id={enrollment_id}")

                    if course_id and enrollment_id:
                        print(f"Attempting to inactivate enrollment {enrollment_id} for student {student} (course {sis_course})")
                        # continue
                        url = f"{BASE_URL}/api/v1/courses/{course_id}/enrollments/{enrollment_id}"
                        try:
                            r = requests.delete(url, headers=HEADERS, data={"task": "inactivate"})
                            r.raise_for_status()
                            print(f"Inactivated enrollment {enrollment_id} for student {student} (course {sis_course})")
                        except Exception as e:
                            # Print response text for debugging when available
                            resp_text = getattr(r, 'text', '') if 'r' in locals() else ''
                            print(f"Failed to inactivate enrollment {enrollment_id} for student {student}: {e} {resp_text}")
                    else:
                        print(f"Missing course_id or enrollment id for student {student}, sis_course_id={sis_course}")
            except:
                # print(student_no, "SIS Course ID not found or invalid SIS Course ID")
                pass
        
    #     count += 1
    #     if  count == 100:
    #         break

    # print(f"Total matches found: {count}")

    # student_no = [
    #     114097,
    #     110575
    # ]

    # for i in student_no:
    #     enrolments = get_active_enrolments(i)
    #     print(f"Enrolments for student {i}: {enrolments}")