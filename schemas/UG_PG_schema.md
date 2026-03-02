I have provided both a **representative JSON example** (populated with data from your first HTML snippet) and the **formal JSON schema** mapping so you can see exactly how the nested arrays and dictionaries are organized.

### Representative PG JSON Example

```json
[
    {
        "file_path": "/Users/sameerbanchhor/Desktop/durg results/datasets/PG/MSC/Biotechnology/First_Semester/33318089001.html",
        "exam_name": "M.Sc. BIOTECHNOLOGY-SEMESTER-1 - DEC-JAN-2018-19",
        "result_declared": "24/04/2019",
        "roll_number": "33318089001",
        "enrollment_no": "DA/2016/45082",
        "name": "BHESHMALA VERMA",
        "student_type": "REGULAR",
        "father_husband_name": "CHINTA RAM VERMA",
        "mother_name": "DHANESHWARI VERMA",
        "college": "333-BHILAI MAHILA MAHAVIDYALAYA , SECTOR-9, BHILAI NAGAR",
        "center": "333-BHILAI MAHILA MAHAVIDYALAYA , SECTOR-9, BHILAI NAGAR",
        "subjects": [
            {
                "subject_code": "101",
                "subject_name": "CELL BIOLOGY",
                "max_marks": "100",
                "min_marks": "20",
                "theory_marks": {
                    "I": "48",
                    "II": "",
                    "III": ""
                },
                "sessional_marks": {
                    "I": "18",
                    "II": "",
                    "III": ""
                },
                "theory_total": "66",
                "practical_marks": {
                    "I": "",
                    "II": "",
                    "sessional": ""
                },
                "subject_total": "66",
                "status": ""
            },
            {
                "subject_code": "105",
                "subject_name": "LAB COURSE - 1 (BASED ON PAPER 1 & 2)",
                "max_marks": "100",
                "min_marks": "20",
                "theory_marks": {
                    "I": "",
                    "II": "",
                    "III": ""
                },
                "sessional_marks": {
                    "I": "",
                    "II": "",
                    "III": ""
                },
                "theory_total": "",
                "practical_marks": {
                    "I": "69",
                    "II": "",
                    "sessional": "19"
                },
                "subject_total": "88",
                "status": ""
            }
        ],
        "grand_max_marks": "600",
        "grand_total_obtained": "417",
        "sgpa": "7.00",
        "result_status": "PASS"
    }
]

```

### JSON Data Model / Schema Breakdown

* **Root Level**: An array of objects `[{...}, {...}]`. Each object represents a single student's complete result document.
* **Student Metadata (Strings)**:
* `file_path`: Absolute path of the scraped file.
* `exam_name`: Title of the examination and semester.
* `result_declared`: Date string.
* `roll_number`: Unique student identifier.
* `enrollment_no`: University registration number.
* `name`: Student's full name.
* `student_type`: Regular, Private, etc.
* `father_husband_name`: Guardian string.
* `mother_name`: Mother's name string.
* `college`: Associated college code and name.
* `center`: Exam center code and name.


* **`subjects` Array**: Contains a list of objects, where each object is a specific row from the marks table.
* `subject_code`: Subject identifier (e.g., "101").
* `subject_name`: Full name of the subject or lab.
* `max_marks`: Maximum possible marks for the subject.
* `min_marks`: Minimum marks required to pass.
* **`theory_marks` Object**:
* `I`: Theory Paper 1 marks.
* `II`: Theory Paper 2 marks.
* `III`: Theory Paper 3 marks.


* **`sessional_marks` Object**:
* `I`: Sessional 1 marks.
* `II`: Sessional 2 marks.
* `III`: Sessional 3 marks.


* `theory_total`: Sum of theory components.
* **`practical_marks` Object**:
* `I`: Practical 1 marks.
* `II`: Practical 2 marks.
* `sessional`: Practical sessional marks.


* `subject_total`: Final obtained marks for the subject.
* `status`: Subject status (e.g., Fail, Pass, Grace), if populated.


* **Final Result Aggregations (Strings)**:
* `grand_max_marks`: The absolute total possible marks across all subjects (e.g., "600").
* `grand_total_obtained`: Sum of all obtained marks.
* `sgpa`: Final Semester Grade Point Average (e.g., "7.00").
* `result_status`: Final textual status (e.g., "PASS", "FAIL", "ATKT").




# 📘 UG JSON Schema Structure

```json
[
  {
    "file_path": "string",
    "roll_number": "string",

    "exam_name": "string",
    "result_declared": "string",

    "enrollment_no": "string",
    "name": "string",
    "student_type": "string",
    "father_husband_name": "string",
    "mother_name": "string",
    "college": "string",
    "center": "string",

    "grand_max_marks": "string",
    "grand_total_obtained": "string",

    "past_years": {
      "first_year_max": "string",
      "first_year_obtained": "string",
      "second_year_max": "string",
      "second_year_obtained": "string"
    },

    "subjects": [
      {
        "subject_code": "string",
        "subject_name": "string",

        "max_marks": "string",
        "min_marks": "string",

        "theory_marks": {
          "I": "string",
          "II": "string",
          "III": "string"
        },

        "sessional_marks": {
          "I": "string",
          "II": "string",
          "III": "string"
        },

        "theory_total": "string",

        "practical_marks": {
          "I": "string",
          "II": "string",
          "sessional": "string"
        },

        "subject_total": "string",
        "status": "string"
      }
    ],

    "result_status": "string"
  }
]
```

---

# 🧠 Important Structural Notes

### ✅ Top Level

* The entire output file is a **JSON array** (`[...]`)
* Each element represents **one student result**

### ✅ `past_years`

* Always exists (as `{}` if no data found)
* May contain:

  * `first_year_max`
  * `first_year_obtained`
  * `second_year_max`
  * `second_year_obtained`

### ✅ `subjects`

* Always an array
* Can be empty (`[]`) if parsing fails
* Each subject has nested marks breakdown

### ✅ All values are stored as:

> **Strings** (even marks are not integers)

