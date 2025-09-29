#!/usr/bin/env python3
"""
Script to create sample Excel files for testing the platform.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_sample_sales_data():
    """Create a sample sales dataset."""
    
    # Generate sample data
    np.random.seed(42)
    n_records = 1000
    
    # Create date range
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range(n_records)]
    
    # Generate sample data
    data = {
        'Date': dates,
        'Customer': np.random.choice(['Acme Corp', 'Tech Solutions', 'Global Industries', 'StartupXYZ', 'MegaCorp'], n_records),
        'Product': np.random.choice(['Widget A', 'Widget B', 'Widget C', 'Gadget X', 'Gadget Y'], n_records),
        'Quantity': np.random.randint(1, 100, n_records),
        'Unit_Price': np.random.uniform(10, 500, n_records),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
        'Sales_Rep': np.random.choice(['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'], n_records)
    }
    
    df = pd.DataFrame(data)
    df['Total_Amount'] = df['Quantity'] * df['Unit_Price']
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    
    return df

def create_sample_employee_data():
    """Create a sample employee dataset."""
    
    np.random.seed(123)
    n_employees = 200
    
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']
    positions = ['Manager', 'Senior', 'Junior', 'Intern']
    
    data = {
        'Employee_ID': [f'EMP{i:04d}' for i in range(1, n_employees + 1)],
        'Name': [f'Employee {i}' for i in range(1, n_employees + 1)],
        'Department': np.random.choice(departments, n_employees),
        'Position': np.random.choice(positions, n_employees),
        'Salary': np.random.normal(75000, 25000, n_employees),
        'Years_Experience': np.random.randint(0, 20, n_employees),
        'Performance_Rating': np.random.choice(['Excellent', 'Good', 'Average', 'Below Average'], n_employees),
        'Hire_Date': pd.date_range('2015-01-01', '2023-12-31', periods=n_employees).strftime('%Y-%m-%d')
    }
    
    df = pd.DataFrame(data)
    df['Salary'] = df['Salary'].round(2)
    
    return df

def create_sample_financial_data():
    """Create a sample financial dataset."""
    
    np.random.seed(456)
    months = pd.date_range('2020-01-01', '2023-12-31', freq='M')
    
    data = {
        'Month': months.strftime('%Y-%m'),
        'Revenue': np.random.normal(100000, 20000, len(months)),
        'Expenses': np.random.normal(80000, 15000, len(months)),
        'Profit': np.random.normal(20000, 10000, len(months)),
        'Customers': np.random.randint(500, 2000, len(months)),
        'Marketing_Spend': np.random.normal(15000, 5000, len(months))
    }
    
    df = pd.DataFrame(data)
    df['Revenue'] = df['Revenue'].round(2)
    df['Expenses'] = df['Expenses'].round(2)
    df['Profit'] = df['Profit'].round(2)
    df['Marketing_Spend'] = df['Marketing_Spend'].round(2)
    
    return df

def main():
    """Create sample Excel files."""
    
    # Create output directory
    output_dir = "sample_data"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Creating sample Excel files...")
    
    # Create sales data
    sales_df = create_sample_sales_data()
    sales_file = os.path.join(output_dir, "sample_sales_data.xlsx")
    with pd.ExcelWriter(sales_file, engine='openpyxl') as writer:
        sales_df.to_excel(writer, sheet_name='Sales', index=False)
        # Add a summary sheet
        summary_data = {
            'Metric': ['Total Records', 'Total Revenue', 'Average Order Value', 'Unique Customers', 'Unique Products'],
            'Value': [
                len(sales_df),
                sales_df['Total_Amount'].sum(),
                sales_df['Total_Amount'].mean(),
                sales_df['Customer'].nunique(),
                sales_df['Product'].nunique()
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"Created: {sales_file}")
    
    # Create employee data
    employee_df = create_sample_employee_data()
    employee_file = os.path.join(output_dir, "sample_employee_data.xlsx")
    with pd.ExcelWriter(employee_file, engine='openpyxl') as writer:
        employee_df.to_excel(writer, sheet_name='Employees', index=False)
        # Add department summary
        dept_summary = employee_df.groupby('Department').agg({
            'Salary': ['count', 'mean', 'sum'],
            'Years_Experience': 'mean'
        }).round(2)
        dept_summary.columns = ['Employee_Count', 'Avg_Salary', 'Total_Salary', 'Avg_Experience']
        dept_summary.to_excel(writer, sheet_name='Department_Summary')
    
    print(f"Created: {employee_file}")
    
    # Create financial data
    financial_df = create_sample_financial_data()
    financial_file = os.path.join(output_dir, "sample_financial_data.xlsx")
    financial_df.to_excel(financial_file, index=False)
    
    print(f"Created: {financial_file}")
    
    print("\nSample files created successfully!")
    print("\nYou can now upload these files to test the platform:")
    print(f"- {sales_file}")
    print(f"- {employee_file}")
    print(f"- {financial_file}")
    
    print("\nSample questions you can try:")
    print("- 'What is the total revenue?'")
    print("- 'Show me sales by region'")
    print("- 'Which employee has the highest salary?'")
    print("- 'What is the average salary by department?'")
    print("- 'Show me the profit trend over time'")

if __name__ == "__main__":
    main()
