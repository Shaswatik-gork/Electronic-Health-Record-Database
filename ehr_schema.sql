-- =============================================================================
-- EHR DATABASE — MySQL Schema + Seed Data (10 Patients)
-- Electronic Health Record Database System
-- Run: mysql -u root -p < ehr_schema.sql
-- NOTE: All patient data is entirely synthetic/fictional for educational use.
-- =============================================================================

DROP DATABASE IF EXISTS ehr_db;
CREATE DATABASE ehr_db;
USE ehr_db;

-- =============================================================================
-- TABLE DEFINITIONS
-- =============================================================================

CREATE TABLE patients (
    patient_id            VARCHAR(10)  PRIMARY KEY,
    full_name             VARCHAR(100) NOT NULL,
    dob                   DATE         NOT NULL,
    gender                ENUM('Male','Female','Other') NOT NULL,
    blood_group           VARCHAR(5),
    allergies             TEXT,
    address               TEXT,
    contact               VARCHAR(15),
    emergency_contact     VARCHAR(100),
    insurance_provider    VARCHAR(100),
    policy_number         VARCHAR(50),
    policy_valid_until    DATE,
    registered_on         DATE,
    last_visit            DATE,
    primary_physician     VARCHAR(100)
);

CREATE TABLE diagnoses (
    diagnosis_id    INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      VARCHAR(10) NOT NULL,
    diagnosis_date  DATE        NOT NULL,
    physician       VARCHAR(100),
    chief_complaint TEXT,
    diagnosis       TEXT,
    assessment      TEXT,
    treatment_plan  TEXT,
    alerts          TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

CREATE TABLE medications (
    med_id          INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      VARCHAR(10)  NOT NULL,
    medication_name VARCHAR(100) NOT NULL,
    dosage          VARCHAR(50),
    frequency       VARCHAR(50),
    prescribed_by   VARCHAR(100),
    prescribed_date DATE,
    is_current      BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

CREATE TABLE lab_results (
    lab_id          INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      VARCHAR(10)  NOT NULL,
    lab_date        DATE         NOT NULL,
    test_name       VARCHAR(100) NOT NULL,
    result_value    VARCHAR(100),
    unit            VARCHAR(50),
    normal_range    VARCHAR(100),
    status          ENUM('Normal','High','Low','Critical') DEFAULT 'Normal',
    ordered_by      VARCHAR(100),
    reviewed        BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

CREATE TABLE admissions (
    admission_id           INT AUTO_INCREMENT PRIMARY KEY,
    patient_id             VARCHAR(10) NOT NULL,
    admitted_on            DATE        NOT NULL,
    discharged_on          DATE,
    ward                   VARCHAR(100),
    room_number            VARCHAR(10),
    reason                 TEXT,
    treatment_given        TEXT,
    discharge_diagnosis    TEXT,
    discharge_instructions TEXT,
    attending_physician    VARCHAR(100),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- =============================================================================
-- PATIENTS (10 records: P-1001 to P-1010)
-- =============================================================================

INSERT INTO patients VALUES
('P-1001','Arjun Mehta','1978-03-14','Male','B+','Penicillin',
 '12 Lakeview Apartments, Banjara Hills, Hyderabad','9876543210',
 'Sunita Mehta (Wife) - 9876543211',
 'Star Health','SH-20234567','2026-12-31','2022-01-05','2026-04-10',
 'Dr. Ramesh Babu (Cardiology)'),

('P-1002','Priya Sharma','1990-07-22','Female','O+','Sulfa drugs, Latex',
 '45 Green Park Colony, Jubilee Hills, Hyderabad','9988776655',
 'Rohit Sharma (Husband) - 9988776656',
 'HDFC ERGO','HE-56781234','2027-03-31','2020-08-18','2026-04-02',
 'Dr. Priya Reddy (Gynecology)'),

('P-1003','Venkat Rao','1955-11-03','Male','A+','None known',
 '7 Senior Citizens Colony, Secunderabad, Hyderabad','9123456789',
 'Kavitha Rao (Daughter) - 9123456790',
 'New India Assurance','NIA-78904321','2026-06-30','2018-03-12','2026-04-15',
 'Dr. Anita Sharma (Neurology)'),

('P-1004','Sneha Iyer','1985-09-18','Female','AB+','Aspirin, NSAIDs',
 '23 Tulip Towers, Gachibowli, Hyderabad','9845671230',
 'Kiran Iyer (Husband) - 9845671231',
 'Bajaj Allianz Health','BA-33219876','2027-08-31','2021-05-10','2026-03-28',
 'Dr. Suresh Kumar (Orthopaedics)'),

('P-1005','Mohammed Farouk','1968-06-25','Male','O-','Codeine',
 '89 Paradise Colony, Toli Chowki, Hyderabad','9701234567',
 'Salma Farouk (Wife) - 9701234568',
 'United India Insurance','UI-44109823','2026-09-30','2019-11-20','2026-04-05',
 'Dr. Ramesh Babu (Cardiology)'),

('P-1006','Lakshmi Devi','1962-02-10','Female','B-','None known',
 '5 Rose Garden, Kukatpally, Hyderabad','9632145870',
 'Srinivas Devi (Son) - 9632145871',
 'Ayushman Bharat (PM-JAY)','PMJAY-56781234','2027-12-31','2017-06-15','2026-04-12',
 'Dr. Venkat Rao (Endocrinology)'),

('P-1007','Rajan Pillai','1995-12-05','Male','A-','None known',
 '67 Cyber Hills, Madhapur, Hyderabad','9876012345',
 'Meena Pillai (Mother) - 9876012346',
 'ICICI Lombard','IL-77654321','2028-01-31','2023-02-14','2026-03-15',
 'Dr. Anita Sharma (Neurology)'),

('P-1008','Deepa Nair','1973-04-30','Female','O+','Penicillin, Sulfa drugs',
 '34 Emerald Heights, Kondapur, Hyderabad','9550123456',
 'Suresh Nair (Husband) - 9550123457',
 'Medi Assist TPA','MA-99012345','2026-11-30','2020-03-22','2026-04-08',
 'Dr. Priya Reddy (Gynecology)'),

('P-1009','Aditya Verma','2001-08-14','Male','B+','None known',
 '11 Sai Nagar, Ameerpet, Hyderabad','9440987654',
 'Ramesh Verma (Father) - 9440987655',
 'Star Health','SH-88123456','2027-06-30','2024-01-09','2026-04-01',
 'Dr. Anita Sharma (Neurology)'),

('P-1010','Geeta Reddy','1980-11-27','Female','AB-','Latex',
 '19 Palm Grove, Miyapur, Hyderabad','9381234567',
 'Naresh Reddy (Husband) - 9381234568',
 'HDFC ERGO','HE-22334455','2027-05-31','2022-07-03','2026-04-14',
 'Dr. Ramesh Babu (Cardiology)');

-- =============================================================================
-- DIAGNOSES (most recent diagnosis for each patient)
-- =============================================================================

INSERT INTO diagnoses (patient_id, diagnosis_date, physician, chief_complaint, diagnosis, assessment, treatment_plan, alerts) VALUES

('P-1001','2026-04-10','Dr. Ramesh Babu',
 'Mild chest discomfort and shortness of breath on exertion for 2 weeks',
 'Hypertensive heart disease with early left ventricular hypertrophy',
 'BP 148/92 mmHg elevated. Echocardiogram shows mild LVH. No acute coronary syndrome.',
 'Increase Amlodipine to 10mg. Add Telmisartan 40mg. Salt restriction. Cardiac rehab. Follow-up 4 weeks.',
 'Monitor potassium — risk of hyperkalaemia with ARB addition.'),

('P-1002','2026-04-02','Dr. Priya Reddy',
 'Irregular menstrual cycles, weight gain 4kg over 3 months, fatigue',
 'PCOS exacerbation with subclinical hypothyroidism worsening',
 'TSH 6.2 mIU/L elevated. LH:FSH ratio 2.8:1. Insulin resistance markers elevated.',
 'Increase Levothyroxine to 75mcg. Continue Metformin. Add Inositol 2g twice daily. Repeat TSH 6 weeks.',
 'Levothyroxine strictly on empty stomach. Avoid calcium within 4 hours.'),

('P-1003','2026-04-15','Dr. Anita Sharma',
 'Increased tremors, difficulty walking, two near-fall episodes in past month',
 'Moderate-stage Parkinson''s Disease with postural instability and mild cognitive decline',
 'UPDRS motor score 34. Bradykinesia pronounced. MMSE 22/30.',
 'Increase Levodopa/Carbidopa to 4x daily. Add Rasagiline 1mg. Physiotherapy. Donepezil to 10mg.',
 'Fall risk HIGH — bed rails, non-slip footwear, home safety assessment required.'),

('P-1004','2026-03-28','Dr. Suresh Kumar',
 'Persistent right knee pain and swelling for 3 months, difficulty climbing stairs',
 'Right knee osteoarthritis Grade III with synovitis',
 'X-ray shows significant joint space narrowing. MRI confirms grade III cartilage loss and synovitis.',
 'Intra-articular steroid injection given. Physiotherapy 3x/week. Weight reduction counselling. '
 'Review 6 weeks — consider total knee replacement if no improvement.',
 'Avoid NSAIDs — allergic to Aspirin and NSAIDs. Use Paracetamol for pain only.'),

('P-1005','2026-04-05','Dr. Ramesh Babu',
 'Recurrent chest tightness, palpitations, and fatigue on mild exertion',
 'Ischaemic cardiomyopathy with reduced ejection fraction (EF 38%)',
 'Echo: EF 38%, dilated LV, regional wall motion abnormality. Previous MI confirmed on scar imaging.',
 'Add Sacubitril/Valsartan 50mg twice daily. Increase Carvedilol to 12.5mg. '
 'Low-sodium diet. Cardiac rehab. ICD evaluation. Follow-up 3 weeks.',
 'Avoid Codeine — patient allergy. Monitor renal function closely with Sacubitril/Valsartan.'),

('P-1006','2026-04-12','Dr. Venkat Rao',
 'Excessive thirst, frequent urination, blurred vision, weight loss of 6kg in 2 months',
 'Newly diagnosed Type 2 Diabetes Mellitus with possible early diabetic retinopathy',
 'FBG 298 mg/dL, HbA1c 11.4%. Fundoscopy: mild non-proliferative diabetic retinopathy changes.',
 'Start Metformin 500mg twice daily. Start Glipizide 5mg once daily before breakfast. '
 'Diabetic diet education. Ophthalmology referral. HbA1c repeat in 3 months.',
 'Covered under Ayushman Bharat — prescriptions must be on approved formulary. '
 'Monitor for hypoglycaemia with Glipizide.'),

('P-1007','2026-03-15','Dr. Anita Sharma',
 'Persistent headaches, dizziness, and two episodes of blurred vision over past 2 weeks',
 'Benign intracranial hypertension (Pseudotumour cerebri)',
 'MRI brain normal. LP opening pressure 28 cmH2O elevated. Visual fields: mild peripheral loss bilateral.',
 'Start Acetazolamide 250mg twice daily. Weight reduction — BMI 31.2. '
 'Ophthalmology referral urgent. Repeat LP in 4 weeks. Avoid Vitamin A supplements.',
 'Monitor for paraesthesia and renal stones — side effects of Acetazolamide.'),

('P-1008','2026-04-08','Dr. Priya Reddy',
 'Heavy and prolonged menstrual bleeding for 6 months, pelvic pressure, urinary frequency',
 'Uterine fibroids (multiple intramural) with menorrhagia and iron deficiency anaemia',
 'USG pelvis: multiple intramural fibroids, largest 5.2cm. Haemoglobin 8.4 g/dL.',
 'Start Ferrous Sulphate 200mg twice daily. Tranexamic acid 500mg three times daily during menstruation. '
 'GnRH analogue (Leuprolide) for fibroid reduction. Gynaecology surgery review 6 weeks.',
 'Allergic to Penicillin and Sulfa drugs — flag for surgical antibiotic prophylaxis.'),

('P-1009','2026-04-01','Dr. Anita Sharma',
 'Recurrent seizures — third episode in 6 months, tonic-clonic type lasting 2-3 minutes',
 'Juvenile myoclonic epilepsy (JME)',
 'EEG: generalised 4-6 Hz polyspike-wave complexes. MRI brain normal. Triggered by sleep deprivation.',
 'Start Sodium Valproate 500mg twice daily. Sleep hygiene education. '
 'Avoid alcohol and sleep deprivation. Driving restriction. Follow-up 4 weeks.',
 'Advise teratogenicity of Valproate if planning a family. Monitor LFTs and platelets at baseline.'),

('P-1010','2026-04-14','Dr. Ramesh Babu',
 'Sudden severe chest pain radiating to left arm, diaphoresis, nausea — onset 2 hours ago',
 'Acute ST-elevation myocardial infarction (STEMI) — anterior wall',
 'ECG: ST elevation V1-V4. Troponin I 18.4 ng/mL Critical. BP 90/60 mmHg on arrival.',
 'Emergency primary PCI — LAD stented successfully. '
 'Dual antiplatelet: Aspirin 75mg + Ticagrelor 90mg twice daily. '
 'Enoxaparin 40mg SC once daily. Atorvastatin 80mg. Cardiac ICU monitoring.',
 'Latex allergy — latex-free protocol throughout. Critical case — daily physician review mandatory.');

-- =============================================================================
-- MEDICATIONS (current medications for all 10 patients)
-- =============================================================================

INSERT INTO medications (patient_id, medication_name, dosage, frequency, prescribed_by, prescribed_date, is_current) VALUES

-- P-1001 Arjun Mehta
('P-1001','Metformin','500mg','Twice daily','Dr. Ramesh Babu','2021-06-01',TRUE),
('P-1001','Amlodipine','10mg','Once daily','Dr. Ramesh Babu','2026-04-10',TRUE),
('P-1001','Atorvastatin','10mg','Once daily at night','Dr. Ramesh Babu','2022-03-01',TRUE),
('P-1001','Telmisartan','40mg','Once daily','Dr. Ramesh Babu','2026-04-10',TRUE),

-- P-1002 Priya Sharma
('P-1002','Levothyroxine','75mcg','Once daily morning fasting','Dr. Priya Reddy','2026-04-02',TRUE),
('P-1002','Metformin','500mg','Once daily','Dr. Priya Reddy','2022-01-15',TRUE),
('P-1002','Vitamin D3','60000 IU','Weekly','Dr. Priya Reddy','2023-05-01',TRUE),
('P-1002','Inositol','2g','Twice daily','Dr. Priya Reddy','2026-04-02',TRUE),

-- P-1003 Venkat Rao
('P-1003','Levodopa/Carbidopa','25/100mg','Four times daily','Dr. Anita Sharma','2026-04-15',TRUE),
('P-1003','Rasagiline','1mg','Once daily','Dr. Anita Sharma','2026-04-15',TRUE),
('P-1003','Donepezil','10mg','Once daily at night','Dr. Anita Sharma','2026-04-15',TRUE),
('P-1003','Calcium + Vitamin D','Standard dose','Twice daily','Dr. Anita Sharma','2022-01-01',TRUE),

-- P-1004 Sneha Iyer
('P-1004','Paracetamol','500mg','Twice daily as needed','Dr. Suresh Kumar','2026-03-28',TRUE),
('P-1004','Pantoprazole','40mg','Once daily before breakfast','Dr. Suresh Kumar','2026-03-28',TRUE),
('P-1004','Calcium Carbonate','500mg','Twice daily with meals','Dr. Suresh Kumar','2025-06-01',TRUE),
('P-1004','Vitamin D3','60000 IU','Once weekly','Dr. Suresh Kumar','2025-06-01',TRUE),

-- P-1005 Mohammed Farouk
('P-1005','Sacubitril/Valsartan','50mg','Twice daily','Dr. Ramesh Babu','2026-04-05',TRUE),
('P-1005','Carvedilol','12.5mg','Twice daily','Dr. Ramesh Babu','2024-08-10',TRUE),
('P-1005','Furosemide','40mg','Once daily morning','Dr. Ramesh Babu','2024-08-10',TRUE),
('P-1005','Spironolactone','25mg','Once daily','Dr. Ramesh Babu','2025-01-15',TRUE),
('P-1005','Atorvastatin','40mg','Once daily at night','Dr. Ramesh Babu','2023-06-01',TRUE),
('P-1005','Aspirin','75mg','Once daily','Dr. Ramesh Babu','2023-06-01',TRUE),

-- P-1006 Lakshmi Devi
('P-1006','Metformin','500mg','Twice daily with meals','Dr. Venkat Rao','2026-04-12',TRUE),
('P-1006','Glipizide','5mg','Once daily before breakfast','Dr. Venkat Rao','2026-04-12',TRUE),
('P-1006','Vitamin B12','500mcg','Once daily','Dr. Venkat Rao','2026-04-12',TRUE),
('P-1006','Multivitamin','Standard dose','Once daily','Dr. Venkat Rao','2026-04-12',TRUE),

-- P-1007 Rajan Pillai
('P-1007','Acetazolamide','250mg','Twice daily','Dr. Anita Sharma','2026-03-15',TRUE),
('P-1007','Paracetamol','500mg','As needed for headache','Dr. Anita Sharma','2026-03-15',TRUE),
('P-1007','Omega-3 Fatty Acids','1000mg','Once daily','Dr. Anita Sharma','2026-03-15',TRUE),

-- P-1008 Deepa Nair
('P-1008','Ferrous Sulphate','200mg','Twice daily after meals','Dr. Priya Reddy','2026-04-08',TRUE),
('P-1008','Tranexamic Acid','500mg','Three times daily during menstruation','Dr. Priya Reddy','2026-04-08',TRUE),
('P-1008','Leuprolide Acetate','3.75mg IM','Once monthly','Dr. Priya Reddy','2026-04-08',TRUE),
('P-1008','Vitamin C','500mg','Once daily','Dr. Priya Reddy','2026-04-08',TRUE),

-- P-1009 Aditya Verma
('P-1009','Sodium Valproate','500mg','Twice daily','Dr. Anita Sharma','2026-04-01',TRUE),
('P-1009','Folic Acid','5mg','Once daily','Dr. Anita Sharma','2026-04-01',TRUE),

-- P-1010 Geeta Reddy
('P-1010','Aspirin','75mg','Once daily','Dr. Ramesh Babu','2026-04-14',TRUE),
('P-1010','Ticagrelor','90mg','Twice daily','Dr. Ramesh Babu','2026-04-14',TRUE),
('P-1010','Atorvastatin','80mg','Once daily at night','Dr. Ramesh Babu','2026-04-14',TRUE),
('P-1010','Enoxaparin','40mg SC','Once daily','Dr. Ramesh Babu','2026-04-14',TRUE),
('P-1010','Ramipril','2.5mg','Once daily','Dr. Ramesh Babu','2026-04-14',TRUE),
('P-1010','Metoprolol','25mg','Twice daily','Dr. Ramesh Babu','2026-04-14',TRUE);

-- =============================================================================
-- LAB RESULTS (recent labs for all 10 patients)
-- =============================================================================

INSERT INTO lab_results (patient_id, lab_date, test_name, result_value, unit, normal_range, status, ordered_by, reviewed) VALUES

-- P-1001 Arjun Mehta
('P-1001','2026-04-08','Fasting Blood Glucose','142','mg/dL','<100','High','Dr. Ramesh Babu',TRUE),
('P-1001','2026-04-08','HbA1c','8.1','%','<7.0 for diabetics','High','Dr. Ramesh Babu',TRUE),
('P-1001','2026-04-08','Serum Creatinine','1.1','mg/dL','0.7-1.2','Normal','Dr. Ramesh Babu',TRUE),
('P-1001','2026-04-08','eGFR','72','mL/min/1.73m2','>90','Low','Dr. Ramesh Babu',TRUE),
('P-1001','2026-04-08','Serum Potassium','4.2','mEq/L','3.5-5.0','Normal','Dr. Ramesh Babu',TRUE),
('P-1001','2026-04-08','Total Cholesterol','218','mg/dL','<200','High','Dr. Ramesh Babu',TRUE),
('P-1001','2026-04-08','LDL','138','mg/dL','<100 for diabetics','High','Dr. Ramesh Babu',TRUE),
('P-1001','2026-04-08','HDL','42','mg/dL','>40','Normal','Dr. Ramesh Babu',TRUE),
('P-1001','2026-04-08','Triglycerides','190','mg/dL','<150','High','Dr. Ramesh Babu',TRUE),
('P-1001','2026-04-08','Haemoglobin','13.8','g/dL','13-17 male','Normal','Dr. Ramesh Babu',TRUE),

-- P-1002 Priya Sharma
('P-1002','2026-04-01','TSH','6.2','mIU/L','0.4-4.5','High','Dr. Priya Reddy',TRUE),
('P-1002','2026-04-01','Free T4','0.82','ng/dL','0.8-1.8','Normal','Dr. Priya Reddy',TRUE),
('P-1002','2026-04-01','LH','11.4','IU/L','2-15','Normal','Dr. Priya Reddy',TRUE),
('P-1002','2026-04-01','FSH','4.1','IU/L','3-10','Normal','Dr. Priya Reddy',TRUE),
('P-1002','2026-04-01','Fasting Insulin','18','uIU/mL','<10','High','Dr. Priya Reddy',TRUE),
('P-1002','2026-04-01','HOMA-IR','4.4','index','<2.5','High','Dr. Priya Reddy',TRUE),
('P-1002','2026-04-01','HbA1c','5.6','%','<5.7','Normal','Dr. Priya Reddy',TRUE),
('P-1002','2026-04-01','Vitamin D','18','ng/mL','>30','Low','Dr. Priya Reddy',TRUE),
('P-1002','2026-04-01','AMH','6.8','ng/mL','1.0-3.5','High','Dr. Priya Reddy',TRUE),
('P-1002','2026-04-01','Prolactin','18','ng/mL','2-29','Normal','Dr. Priya Reddy',TRUE),

-- P-1003 Venkat Rao
('P-1003','2026-04-14','Haemoglobin','11.8','g/dL','13-17 male','Low','Dr. Anita Sharma',TRUE),
('P-1003','2026-04-14','Serum Creatinine','1.3','mg/dL','0.7-1.2','High','Dr. Anita Sharma',TRUE),
('P-1003','2026-04-14','eGFR','58','mL/min/1.73m2','>90','Low','Dr. Anita Sharma',TRUE),
('P-1003','2026-04-14','Serum Albumin','3.4','g/dL','3.5-5.0','Low','Dr. Anita Sharma',TRUE),
('P-1003','2026-04-14','Homocysteine','18','umol/L','<15','High','Dr. Anita Sharma',TRUE),
('P-1003','2026-04-14','Vitamin B12','198','pg/mL','200-900','Low','Dr. Anita Sharma',TRUE),
('P-1003','2026-04-14','Fasting Glucose','88','mg/dL','70-100','Normal','Dr. Anita Sharma',TRUE),
('P-1003','2026-04-14','Serum Calcium','8.6','mg/dL','8.5-10.5','Normal','Dr. Anita Sharma',TRUE),

-- P-1004 Sneha Iyer
('P-1004','2026-03-25','Haemoglobin','12.1','g/dL','12-16 female','Normal','Dr. Suresh Kumar',TRUE),
('P-1004','2026-03-25','ESR','48','mm/hr','<20','High','Dr. Suresh Kumar',TRUE),
('P-1004','2026-03-25','CRP','18.4','mg/L','<5','High','Dr. Suresh Kumar',TRUE),
('P-1004','2026-03-25','Rheumatoid Factor','Negative','','Negative','Normal','Dr. Suresh Kumar',TRUE),
('P-1004','2026-03-25','Uric Acid','5.2','mg/dL','2.4-6.0 female','Normal','Dr. Suresh Kumar',TRUE),
('P-1004','2026-03-25','Vitamin D','22','ng/mL','>30','Low','Dr. Suresh Kumar',TRUE),
('P-1004','2026-03-25','Calcium','9.1','mg/dL','8.5-10.5','Normal','Dr. Suresh Kumar',TRUE),
('P-1004','2026-03-25','Fasting Glucose','92','mg/dL','70-100','Normal','Dr. Suresh Kumar',TRUE),

-- P-1005 Mohammed Farouk
('P-1005','2026-04-03','BNP','820','pg/mL','<100','High','Dr. Ramesh Babu',TRUE),
('P-1005','2026-04-03','Troponin I','0.08','ng/mL','<0.04','High','Dr. Ramesh Babu',TRUE),
('P-1005','2026-04-03','Serum Creatinine','1.6','mg/dL','0.7-1.2','High','Dr. Ramesh Babu',TRUE),
('P-1005','2026-04-03','eGFR','48','mL/min/1.73m2','>90','Low','Dr. Ramesh Babu',TRUE),
('P-1005','2026-04-03','Serum Potassium','5.1','mEq/L','3.5-5.0','Normal','Dr. Ramesh Babu',TRUE),
('P-1005','2026-04-03','Serum Sodium','132','mEq/L','136-145','Low','Dr. Ramesh Babu',TRUE),
('P-1005','2026-04-03','Haemoglobin','11.2','g/dL','13-17 male','Low','Dr. Ramesh Babu',TRUE),
('P-1005','2026-04-03','LDL','110','mg/dL','<70 for CAD','High','Dr. Ramesh Babu',TRUE),

-- P-1006 Lakshmi Devi
('P-1006','2026-04-10','Fasting Blood Glucose','298','mg/dL','70-100','Critical','Dr. Venkat Rao',TRUE),
('P-1006','2026-04-10','HbA1c','11.4','%','<7.0 for diabetics','High','Dr. Venkat Rao',TRUE),
('P-1006','2026-04-10','Postprandial Glucose','380','mg/dL','<140','Critical','Dr. Venkat Rao',TRUE),
('P-1006','2026-04-10','Serum Creatinine','0.9','mg/dL','0.5-1.1 female','Normal','Dr. Venkat Rao',TRUE),
('P-1006','2026-04-10','Haemoglobin','10.8','g/dL','12-16 female','Low','Dr. Venkat Rao',TRUE),
('P-1006','2026-04-10','Total Cholesterol','242','mg/dL','<200','High','Dr. Venkat Rao',TRUE),
('P-1006','2026-04-10','Triglycerides','310','mg/dL','<150','High','Dr. Venkat Rao',TRUE),
('P-1006','2026-04-10','Vitamin B12','280','pg/mL','200-900','Normal','Dr. Venkat Rao',TRUE),

-- P-1007 Rajan Pillai
('P-1007','2026-03-12','Haemoglobin','14.5','g/dL','13-17 male','Normal','Dr. Anita Sharma',TRUE),
('P-1007','2026-03-12','CSF Opening Pressure','28','cmH2O','<20','High','Dr. Anita Sharma',TRUE),
('P-1007','2026-03-12','CSF Protein','32','mg/dL','15-45','Normal','Dr. Anita Sharma',TRUE),
('P-1007','2026-03-12','CSF Glucose','62','mg/dL','50-80','Normal','Dr. Anita Sharma',TRUE),
('P-1007','2026-03-12','Serum Vitamin A','98','mcg/dL','20-60','High','Dr. Anita Sharma',TRUE),
('P-1007','2026-03-12','Fasting Glucose','96','mg/dL','70-100','Normal','Dr. Anita Sharma',TRUE),
('P-1007','2026-03-12','BMI value','31.2','kg/m2','18.5-24.9','High','Dr. Anita Sharma',TRUE),

-- P-1008 Deepa Nair
('P-1008','2026-04-05','Haemoglobin','8.4','g/dL','12-16 female','Low','Dr. Priya Reddy',TRUE),
('P-1008','2026-04-05','Serum Ferritin','6','ng/mL','12-150','Low','Dr. Priya Reddy',TRUE),
('P-1008','2026-04-05','Serum Iron','38','ug/dL','60-170','Low','Dr. Priya Reddy',TRUE),
('P-1008','2026-04-05','TIBC','420','ug/dL','250-370','High','Dr. Priya Reddy',TRUE),
('P-1008','2026-04-05','TSH','2.8','mIU/L','0.4-4.5','Normal','Dr. Priya Reddy',TRUE),
('P-1008','2026-04-05','CA-125','28','U/mL','<35','Normal','Dr. Priya Reddy',TRUE),
('P-1008','2026-04-05','WBC','7200','per uL','4000-11000','Normal','Dr. Priya Reddy',TRUE),
('P-1008','2026-04-05','Platelets','245000','per uL','150000-400000','Normal','Dr. Priya Reddy',TRUE),

-- P-1009 Aditya Verma
('P-1009','2026-03-28','Haemoglobin','14.2','g/dL','13-17 male','Normal','Dr. Anita Sharma',TRUE),
('P-1009','2026-03-28','ALT (Liver)','28','U/L','7-56','Normal','Dr. Anita Sharma',TRUE),
('P-1009','2026-03-28','AST (Liver)','32','U/L','10-40','Normal','Dr. Anita Sharma',TRUE),
('P-1009','2026-03-28','Platelet Count','210000','per uL','150000-400000','Normal','Dr. Anita Sharma',TRUE),
('P-1009','2026-03-28','Fasting Glucose','88','mg/dL','70-100','Normal','Dr. Anita Sharma',TRUE),
('P-1009','2026-03-28','EEG Result','Abnormal - polyspike-wave 4-6Hz','','Normal background','High','Dr. Anita Sharma',TRUE),
('P-1009','2026-03-28','Valproate Level (baseline)','Not started','mcg/mL','50-100 therapeutic','Normal','Dr. Anita Sharma',FALSE),

-- P-1010 Geeta Reddy
('P-1010','2026-04-14','Troponin I','18.4','ng/mL','<0.04','Critical','Dr. Ramesh Babu',TRUE),
('P-1010','2026-04-14','CK-MB','88','U/L','<25','Critical','Dr. Ramesh Babu',TRUE),
('P-1010','2026-04-14','BNP','650','pg/mL','<100','High','Dr. Ramesh Babu',TRUE),
('P-1010','2026-04-14','Haemoglobin','11.5','g/dL','12-16 female','Low','Dr. Ramesh Babu',TRUE),
('P-1010','2026-04-14','Serum Potassium','3.8','mEq/L','3.5-5.0','Normal','Dr. Ramesh Babu',TRUE),
('P-1010','2026-04-14','Serum Creatinine','1.0','mg/dL','0.5-1.1 female','Normal','Dr. Ramesh Babu',TRUE),
('P-1010','2026-04-14','LDL','168','mg/dL','<70 for STEMI','High','Dr. Ramesh Babu',TRUE),
('P-1010','2026-04-14','Total Cholesterol','235','mg/dL','<200','High','Dr. Ramesh Babu',TRUE),
('P-1010','2026-04-14','Fasting Glucose','156','mg/dL','70-100','High','Dr. Ramesh Babu',FALSE),
('P-1010','2026-04-14','INR','1.1','','0.8-1.2','Normal','Dr. Ramesh Babu',TRUE);

-- =============================================================================
-- ADMISSIONS (historical and current admissions for all 10 patients)
-- =============================================================================

INSERT INTO admissions (patient_id, admitted_on, discharged_on, ward, room_number, reason, treatment_given, discharge_diagnosis, discharge_instructions, attending_physician) VALUES

-- P-1001 Arjun Mehta (2 admissions)
('P-1001','2023-01-12','2023-01-15','Cardiology','204',
 'Acute chest pain — rule out ACS',
 'IV fluids, ECG monitoring, troponin serial (negative x3), stress echo (negative)',
 'Non-cardiac chest pain, hypertensive urgency',
 'Continue medications, low-salt diet, cardiology follow-up in 2 weeks',
 'Dr. Ramesh Babu'),

('P-1001','2024-11-18','2024-11-20','General Medicine','312',
 'Hypoglycaemic episode — BG 52 mg/dL, found unresponsive at home',
 'IV Dextrose 50% stat, BG monitoring every 2 hours, Metformin dose reviewed',
 'Hypoglycaemia secondary to Metformin — dose adjusted',
 'Metformin reduced, diabetes education, glucometer provided, endocrinology referral',
 'Dr. Ramesh Babu'),

-- P-1002 Priya Sharma (1 admission)
('P-1002','2025-02-14','2025-02-16','Gynecology','108',
 'Elective laparoscopic right ovarian cystectomy — 8cm endometrioma',
 'Laparoscopic surgery under GA — no complications. Mobilised Day 1.',
 'Benign endometriotic cyst — histopathology no malignancy',
 'Rest 1 week, no heavy lifting 4 weeks, pelvic floor exercises, follow-up 6 weeks',
 'Dr. Priya Reddy'),

-- P-1003 Venkat Rao (3 admissions)
('P-1003','2021-03-10','2021-03-12','Orthopaedics','205',
 'Fall injury — right hip bruise',
 'X-ray hip (no fracture), Paracetamol, physiotherapy assessment',
 'Soft tissue right hip injury — conservative management',
 'Rest, analgesia, fall prevention counselling, walking frame assessment',
 'Dr. Suresh Kumar'),

('P-1003','2022-09-05','2022-09-08','Neurology','301',
 'Parkinson''s medication adjustment — wearing-off phenomenon',
 'Levodopa timing review, dose adjustment, physiotherapy, occupational therapy',
 'Parkinson''s disease — medication regimen optimised',
 'New medication schedule given, follow-up 4 weeks',
 'Dr. Anita Sharma'),

('P-1003','2025-01-08','2025-01-13','General Medicine','310',
 'Community-acquired pneumonia — fever 39.2C, productive cough, SpO2 91%',
 'IV Ceftriaxone, oxygen therapy 2L/min, chest physiotherapy, nebulisation',
 'Community-acquired pneumonia — resolved',
 'Oral Amoxicillin-Clavulanate 5 days, rest, follow-up 2 weeks',
 'Dr. Anita Sharma'),

-- P-1004 Sneha Iyer (1 admission)
('P-1004','2024-07-20','2024-07-21','Orthopaedics','110',
 'Acute right knee swelling and pain — unable to weight bear',
 'Joint aspiration (80mL fluid), intra-articular steroid injection, immobilisation',
 'Acute synovitis — right knee osteoarthritis flare',
 'RICE protocol, Paracetamol, physiotherapy, follow-up 3 weeks',
 'Dr. Suresh Kumar'),

-- P-1005 Mohammed Farouk (2 admissions)
('P-1005','2023-05-15','2023-05-22','Cardiac ICU','ICU-2',
 'Acute decompensated heart failure — severe dyspnoea, SpO2 84%, bilateral crackles',
 'IV Furosemide, IV Dobutamine, BiPAP support, daily weights, fluid restriction 1.5L/day',
 'Acute decompensated ischaemic cardiomyopathy — stabilised',
 'Home on oral diuretics, daily weight monitoring, fluid restriction, weekly follow-up',
 'Dr. Ramesh Babu'),

('P-1005','2025-08-03','2025-08-10','Cardiology','206',
 'ICD implantation — sustained ventricular tachycardia episode',
 'Dual-chamber ICD implanted successfully. Wound clean. Device interrogation normal.',
 'Ischaemic cardiomyopathy — ICD implanted for primary prevention',
 'ICD care instructions, avoid MRI, device clinic 6 weeks, driving restriction 4 weeks',
 'Dr. Ramesh Babu'),

-- P-1006 Lakshmi Devi (1 admission)
('P-1006','2026-04-12','2026-04-15','General Medicine','315',
 'Newly diagnosed diabetes — HbA1c 11.4%, FBG 298 mg/dL — admitted for stabilisation',
 'IV insulin infusion Day 1, transition to oral hypoglycaemics, dietitian review, diabetes education',
 'Type 2 Diabetes Mellitus newly diagnosed — glucose stabilised on discharge',
 'Metformin + Glipizide started, diabetic diet sheet, glucometer training, follow-up 2 weeks',
 'Dr. Venkat Rao'),

-- P-1007 Rajan Pillai (1 admission)
('P-1007','2026-03-10','2026-03-12','Neurology','302',
 'Severe headache with blurred vision — urgent LP performed',
 'Lumbar puncture (opening pressure 28 cmH2O), CSF analysis, IV Acetazolamide loading, ophthalmology review',
 'Benign intracranial hypertension — LP therapeutic and diagnostic',
 'Oral Acetazolamide, weight loss advice, ophthalmology follow-up 2 weeks, avoid Vitamin A',
 'Dr. Anita Sharma'),

-- P-1008 Deepa Nair (1 admission)
('P-1008','2025-06-18','2025-06-19','Gynecology','109',
 'Severe menorrhagia — soaking more than 10 pads/day, Haemoglobin 7.1 g/dL',
 'IV iron infusion (Ferric Carboxymaltose 1g), 1 unit PRBC transfusion, Tranexamic acid IV',
 'Severe menorrhagia with iron deficiency anaemia — uterine fibroids',
 'Oral iron supplements, Tranexamic acid during periods, Gynaecology surgery planning',
 'Dr. Priya Reddy'),

-- P-1009 Aditya Verma (1 admission)
('P-1009','2026-03-28','2026-03-30','Neurology','304',
 'Generalised tonic-clonic seizure lasting 3 minutes — third episode in 6 months',
 'Post-ictal monitoring, EEG, MRI brain (normal), Valproate IV loading, neuropsychology referral',
 'Juvenile myoclonic epilepsy — diagnosed and treated',
 'Sodium Valproate oral, driving restricted, sleep hygiene education, follow-up 4 weeks',
 'Dr. Anita Sharma'),

-- P-1010 Geeta Reddy (currently admitted — discharged_on IS NULL)
('P-1010','2026-04-14',NULL,'Cardiac ICU','ICU-1',
 'Acute STEMI — anterior wall, onset 2 hours, brought by ambulance',
 'Emergency primary PCI — LAD stented. Dual antiplatelet started. Cardiac monitoring ongoing.',
 NULL,
 NULL,
 'Dr. Ramesh Babu');
-- P-1010 is CURRENTLY ADMITTED (no discharge date yet)
