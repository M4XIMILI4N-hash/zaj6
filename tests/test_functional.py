import pytest
from src.models import Parameters
from src.manager import Manager

@pytest.fixture
def manager():

    params = Parameters(
        apartments_json_path="data/apartments.json",
        tenants_json_path="data/tenants.json",
        transfers_json_path="data/transfers.json",
        bills_json_path="data/bills.json"
    )
    return Manager(params)
def test_tenant_settlements_sum_equals_apartment_costs(manager):
    
    apartment_id = 'apart-polanka' 

    year = 2025 
    month = 1
    
    apartment_settlement = manager.get_settlement(apartment_id, year, month)
    
    assert apartment_settlement is not None, "Rozliczenie mieszkania nie zostało utworzone."
    
    tenant_settlements = manager.create_tenants_settlements(apartment_settlement)
    
    assert tenant_settlements is not None, "Nie udało się utworzyć rozliczeń dla lokatorów."
    
    total_tenants_due = sum(tenant.total_due_pln for tenant in tenant_settlements)
    total_apartment_costs = apartment_settlement.total_due_pln 
    
    assert total_tenants_due == total_apartment_costs, (
        f"Błąd integralności! Suma obciążeń lokatorów ({total_tenants_due} PLN) "
        f"nie zgadza się z kosztami mieszkania ({total_apartment_costs} PLN)."
    )


def test_get_debtors_report_returns_correct_debts(manager):

    debtors_report = manager.get_debtors_report()

    assert isinstance(debtors_report, dict), "Raport dłużników powinien być słownikiem (dict)."
    

    assert debtors_report, "Raport dłużników nie powinien być pusty dla danych testowych."

    for tenant_name, debt_amount in debtors_report.items():
        assert debt_amount > 0, (
            f"Błąd logiki: Lokator {tenant_name} znalazł się w raporcie dłużników, "
            f"ale jego 'dług' wynosi {debt_amount} PLN!"
        )



def test_get_tax_calculates_correct_amount(manager):


    year = 2023
    month = 10
    tax_rate = 0.085 # Ryczałt 8.5%
    
 
    tax_to_pay = manager.get_tax(year, month, tax_rate)
    

    assert isinstance(tax_to_pay, int), "Podatek powinien być zaokrąglony do pełnych złotych (int)."
    assert tax_to_pay >= 0, "Podatek nie może być ujemny."


def test_get_annual_report_aggregates_data(manager):

    year = 2023
    

    report = manager.get_annual_report(year)

    assert isinstance(report, dict), "Raport roczny powinien być słownikiem."
    assert 'incomes' in report, "Raport musi zawierać klucz 'incomes'."
    assert 'costs' in report, "Raport musi zawierać klucz 'costs'."
    
    
    assert report['incomes'] >= 0
    assert report['costs'] >= 0