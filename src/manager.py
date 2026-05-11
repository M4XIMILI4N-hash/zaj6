from src.models import Apartment, Bill, Parameters, Tenant, TenantSettlement, Transfer, ApartmentSettlement
from typing import List, Tuple

class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int = None, month: int = None) -> float | None:
        if month is not None and (month < 1 or month > 12):
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key and (year is None or bill.settlement_year == year) and (month is None or bill.settlement_month == month):
                total_cost += bill.amount_pln
        return total_cost

    def get_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_key not in self.apartments:
            return None
        total_cost = self.get_apartment_costs(apartment_key, year, month)
        if total_cost is None:
            return None
        
        return ApartmentSettlement(
            key=f"{apartment_key}-{year}-{month}",
            apartment=apartment_key,
            year=year,
            month=month,
            total_due_pln=total_cost
        )
    
    def create_tenants_settlements(self, apartment_settlement: ApartmentSettlement) -> List[TenantSettlement] | None:
        if apartment_settlement.month < 1 or apartment_settlement.month > 12:
            raise ValueError("Month must be between 1 and 12")
        if apartment_settlement.apartment not in self.apartments:
            return None
        tenants_in_apartment = [tenant for tenant in self.tenants.values() if tenant.apartment == apartment_settlement.apartment]
        if not tenants_in_apartment:
            return []
        
        return [
            TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=apartment_settlement.key,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                total_due_pln=apartment_settlement.total_due_pln / len(tenants_in_apartment)
            )
        for tenant in tenants_in_apartment ] 
    
    def get_debtors_report(self) -> dict:

            tenant_dues = {}  
            tenant_paid = {} 
            
        
            settlement_periods = set()
            for bill in self.bills:
                settlement_periods.add((bill.apartment, bill.settlement_year, bill.settlement_month))
                
    
            for apt_key, year, month in settlement_periods:
                apt_settlement = self.get_settlement(apt_key, year, month)
                if apt_settlement:
                    tenants_settlements = self.create_tenants_settlements(apt_settlement)
                    if tenants_settlements:
                        for ts in tenants_settlements:
                    
                            tenant_dues[ts.tenant] = tenant_dues.get(ts.tenant, 0.0) + ts.total_due_pln
                            
    
            for transfer in self.transfers:
                
                tenant_name = transfer.tenant 
                tenant_paid[tenant_name] = tenant_paid.get(tenant_name, 0.0) + transfer.amount_pln
                

            debtors_report = {}
            for tenant, due_amount in tenant_dues.items():
                paid_amount = tenant_paid.get(tenant, 0.0)
                debt = due_amount - paid_amount

                if debt > 0.01:
                    debtors_report[tenant] = round(debt, 2)
                    
            return debtors_report

    
    def get_tax(self, year: int, month: int, tax_rate: float) -> int:

        total_income = 0.0
        
        for transfer in self.transfers:
            
            if transfer.settlement_year == year and transfer.settlement_month == month:
                total_income += transfer.amount_pln
                
        tax_amount = round(total_income * tax_rate)
        return tax_amount

    def get_annual_report(self, year: int) -> dict:

        total_incomes = 0.0
        total_costs = 0.0
        
  
        for transfer in self.transfers:
       
            if transfer.settlement_year == year:
                total_incomes += transfer.amount_pln
                
      
        for bill in self.bills:
            if bill.settlement_year == year:
                total_costs += bill.amount_pln
                
        return {
            'year': year,
            'incomes': round(total_incomes, 2),
            'costs': round(total_costs, 2),
            'profit': round(total_incomes - total_costs, 2)
        }