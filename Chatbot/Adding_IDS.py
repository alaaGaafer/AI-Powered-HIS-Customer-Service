import pandas as pd

# Load Excel file
file_path = "excel_sheets/Xyris HIS_data.xlsx"
xls = pd.ExcelFile(file_path)

# Read sheets
physicians_df = pd.read_excel(xls, sheet_name="Physicians")
schedules_df = pd.read_excel(xls, sheet_name="Schedules")
specialities_df = pd.read_excel(xls, sheet_name="Specialities")
Pricelist_df = pd.read_excel(xls, sheet_name="Pricelist")

# Assign Unique IDs to Doctors
unique_doctors = physicians_df["Name"].unique()
doctor_id_mapping = {name: idx + 1 for idx, name in enumerate(unique_doctors)}

# Map ID to Doctor Name in Physicians & Schedules sheets
physicians_df["Doctor ID"] = physicians_df["Name"].map(doctor_id_mapping)
schedules_df["Doctor ID"] = schedules_df["Doctor Name"].map(doctor_id_mapping)


# Assign Unique IDs to Specialities
unique_specialities = specialities_df["Speciality Name"].unique()
speciality_id_mapping = {name: idx + 1 for idx, name in enumerate(unique_specialities)}

# Map ID to Speciality Name in Specialities sheet
specialities_df["Speciality ID"] = specialities_df["Speciality Name"].map(speciality_id_mapping)

# Assign Unique IDs to Pricelist
unique_services = Pricelist_df["Service Name"].unique()
services_id_mapping = {name: idx + 1 for idx, name in enumerate(unique_services)}

# Map ID to Service Name in Pricelist sheet
Pricelist_df["Service ID"] = Pricelist_df["Service Name"].map(services_id_mapping)




# Save the updated Excel file
with pd.ExcelWriter("excel_sheets/updated_Xyris HIS_data.xlsx") as writer:
    physicians_df.to_excel(writer, sheet_name="Physicians", index=False)
    schedules_df.to_excel(writer, sheet_name="Schedules", index=False)
    specialities_df.to_excel(writer, sheet_name="Specialities", index=False)
    Pricelist_df.to_excel(writer, sheet_name="Pricelist", index=False)


print("Excel file updated successfully!")

#
