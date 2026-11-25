from __future__ import annotations
import math
import numpy as np
import pandas as pd

def calculate_model(config: dict, reuse_fraction=None, cost_per_person_month=None, multiplier_scale=1.0):
    fp=config["functional_points"]; k=config["kloc_per_1000_fp"]; reuse=config["reuse_fraction"] if reuse_fraction is None else reuse_fraction
    kloc=fp*k/1000*(1-reuse)
    sf=config["scale_factors"]; sum_sf=sum(sf.values())
    B=config["cocomo"]["B_base"]+config["cocomo"]["scale_step"]*sum_sf
    em=config["effort_multipliers"]
    active_em={name:value for name,value in em.items() if value != 0}
    em_total=math.prod(active_em.values())*multiplier_scale
    A=config["cocomo"]["A"]; effort=A*(kloc**B)*em_total
    tdev=config["cocomo"]["duration_coefficient"]*(effort**config["cocomo"]["duration_exponent"])
    rate=config["costs"]["cost_per_person_month_rub"] if cost_per_person_month is None else cost_per_person_month
    direct=effort*rate; overhead=direct*config["costs"]["overhead_rate"]; before_vat=direct+overhead; vat=before_vat*config["costs"]["vat_rate"]; total=before_vat+vat
    return {'functional_points':fp,'reuse_fraction':reuse,'kloc':kloc,'sum_sf':sum_sf,'B':B,'active_em':active_em,'inactive_em':[name for name,value in em.items() if value==0],'em_total':em_total,'effort_pm':effort,'tdev_months':tdev,'cost_per_person_month':rate,'direct_cost_rub':direct,'overhead_rub':overhead,'cost_before_vat_rub':before_vat,'vat_rub':vat,'total_cost_rub':total}

def calculate_moscow_model(config: dict):
    m=config["moscow_comparison"]; size=config["functional_points"]*config["kloc_per_1000_fp"]/1000
    mt_product=math.prod(value for value in m["mt_factors"].values() if value != 0)
    effort=m["coefficient_A"]*(size**m["coefficient_B"])*mt_product
    planned_duration=m["planned_duration_months"]
    roles=m["roles"]; role_coeff_sum=sum(role["headcount_coefficient"] for role in roles)
    headcount_ratio=effort/planned_duration
    headcount=headcount_ratio*role_coeff_sum
    qualification=sum(role["headcount_coefficient"]*role["salary_index"] for role in roles)/role_coeff_sum
    average_output=m["salary_base_rub"]*m["conversion_coefficient"]*(1+m["profitability_rate"])/m["salary_share_coefficient"]
    cost_before_vat=average_output*planned_duration*headcount*qualification
    vat=cost_before_vat*m["vat_rate"]; total=cost_before_vat+vat
    return {"size_kloc":size,"mt_product":mt_product,"effort_pm":effort,"planned_duration_months":planned_duration,"headcount_ratio":headcount_ratio,"role_coeff_sum":role_coeff_sum,"headcount":headcount,"qualification_coefficient":qualification,"average_output_rub":average_output,"cost_before_vat_rub":cost_before_vat,"vat_rub":vat,"total_cost_rub":total,"mt_factors":m["mt_factors"]}

def format_rub(value, decimals=0): return f'{value:,.{decimals}f}'.replace(',',' ').replace('.',',')
def format_mln(value, decimals=1): return format_rub(value/1_000_000, decimals)
