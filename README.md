# 🏥 Hospital Information System Web Application

## 🔬 Ophthalmology Department

---

## 📌 Project Overview

This project is a **Hospital Information System (HIS)** web application built using **Django**, focusing on the **Ophthalmology Department**.

It is designed to simulate real-world hospital workflows, enabling secure interactions between **patients**, **doctors**, and **administrative users**, along with features such as:

- Appointment scheduling  
- Report and prescription generation  
- Profile management  
- Cloud-hosted assets  
- Admin-level statistics and monitoring  

The system is fully **role-based**, dynamic, and responsive for all device types.

---

## 🧩 Key Features

- 🌐 **Home Page** accessible to all visitors  
- 🔐 **User Registration and Login** with role-based access (Patients, Doctors, Admins)  
- 🧠 **Forgot Password Functionality**:  
  Users can request a verification code via email to **reset their password securely**  
- 👤 **Individual Profile Pages** for Doctors and Patients  
- 🩺 **Appointments**: Patients can book and manage doctor appointments  
- 📁 **Medical Report Generation** and **Prescription Records**  
- ✉️ **Contact Us Form** for user inquiries and feedback  
- ☁️ **Cloud-Hosted Images**: All images and medical scans are stored in the cloud, making them globally accessible on the website  

---

## 🛠️ Technologies Used

**Backend:**  
- Django (Python)

**Frontend:**  
- HTML, CSS, JavaScript  
- Bootstrap (for responsive design)

**Database:**  
- PostgreSQL  
- Hosted on Neon– a serverless database platform

**Cloud Storage:**  
- Images and static assets are hosted in the cloud to ensure fast, global availability for presentations and public viewing

---

## 🗃️ Database Design – ER Diagram

We have designed a robust and normalized **Entity-Relationship (ER) Diagram** tailored to the **Ophthalmology Department**.

### 📌 Core Entities

- **USER** – Shared attributes for all user roles (Patient, Doctor, Admin)  
- **PATIENT** – Medical records, emergency contacts, insurance, etc.  
- **DOCTOR** – Credentials, specialization, consultation fees, and experience  
- **ADMIN** – Role-based system management users  
- **APPOINTMENT** – Tracks scheduling, status, and linkage between patients and doctors  
- **REPORT** – Summary of each appointment, diagnosis, and recommendations  
- **PRESCRIPTION_GLASSES** – Prescription records for ophthalmic lenses  
- **BILLING** – Payment details, insurance coverage, and status tracking  

Each entity is connected with properly defined relationships, enforcing **data integrity** and **real-world logic**.

---

## 🚀 Phase 1 Deliverables

In **Phase 1**, we accomplished the following:

- ✅ Completed the **full ER diagram** and **relational schema** design  
- 🔐 Developed **user registration and login** with email-based password reset (verification code sent)  
- 👥 Created **profile pages** for Patients and Doctors with detailed fields  
- 🧱 Implemented database models using Django  
- 💻 Designed responsive frontend pages using **Bootstrap**  
- ☁️ Uploaded all images to cloud storage to support **global accessibility and presentations**

---

## 🎥 Demo
- 📂 [Full Website Demo – End-to-End Testing](https://drive.google.com/file/d/1sG45P6kPtVC--BfTqkdU2HMvYHybOtAP/view?usp=drive_link)

