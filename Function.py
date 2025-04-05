import re
import pandas as pd
def dressing_value(block, df1, df2):
    # Fetch block color and month safely
    block_data = df1[df1['BLOCK NO'] == block]
    # print("this is the block_data",block_data)
    
    if block_data.empty:
        return None, 0, None  # Return defaults if no data found

    block_colour = block_data['COLOUR'].iloc[0]
    month = block_data['MONTH'].iloc[0]
    
    # Compute total square meters
    qty = block_data["TOTAL SQM"].sum()

    def get_cost(item):
        """Fetches cost per SFT safely, returns 0 if not found."""
        cost_series = df2[(df2['MONTH'] == month) & (df2['ITEM'] == item)]['COST PER SFT']
        return cost_series.sum() if not cost_series.empty else 0

    # Calculate costs
    price = round(qty * get_cost("MONOWIRE SAW"),0)

    return block_colour, price, month
#function to calculate the cutting qty and cutting cost and misc cost
def cutting_value(block, df1, df2, month):

    dff1 = df1[df1['BLOCK NO'].str.contains(fr'^{block}\s*[A-Z]?$', na=False, regex=True)]
    # print("cutting data","\n","month:",month,"\n",dff1)
    # print("cutting_valuedfff",dff1)

    mws_qty = dff1[dff1['MACHINE'] == "MWS"]['AREA IN SQFT'].sum()
    no_mws_qty = dff1[dff1['MACHINE'] != "MWS"]['AREA IN SQFT'].sum()

    def get_cost(item_name, process_name=None):
        """Fetches cost per SFT safely, returns 0 if not found."""
        if process_name:
            cost_series = df2[(df2['MONTH'] == month) & (df2['PROCESS'] == process_name)]['COST PER SFT']
        else:
            cost_series = df2[(df2['MONTH'] == month) & (df2['ITEM'] == item_name)]['COST PER SFT']
            # print("this else condition executed:",
                #   '\n',cost_series)
        return cost_series.sum() if not cost_series.empty else 0

    misc_cost = round((mws_qty + no_mws_qty) * get_cost(item_name=None,process_name="MISC"),0)
    # print(misc_cost,"misc cost")
    mws_price = mws_qty * get_cost("MULTI WIRE SAW")
    no_mws_price = no_mws_qty * get_cost("CUTTER")
    salary = (mws_qty + no_mws_qty) * get_cost("SALARY")

    total_cost = round(mws_price + no_mws_price + salary,0)
    # print("cutting cost costing",total_cost)
    total_area = round(mws_qty + no_mws_qty,0)

    # print("cutting_value", total_area, total_cost, misc_cost)
    
    return total_area, total_cost, misc_cost

def polishing_value(block, df1, df2, month):
    dff1 = df1[df1['BLOCK NO'].str.contains(fr'^{block}\s*[A-Z]?$', na=False, regex=True)]
    # print("this ths the polishing dataframe have the regex dff1",dff1)
    grinding_qty = dff1[dff1['PROCESS CATEGORY'] == "GRINDING"]['SFT'].sum()
    polishing_qty = dff1[dff1['PROCESS CATEGORY'] == "POLISHING"]['SFT'].sum()
    leather_honed_qty = dff1[dff1['PROCESS CATEGORY'] == "LEATHER ADN HONED"]['SFT'].sum()
    # print("polishing aty",grinding_qty,polishing_qty,leather_honed_qty)

    def get_cost(process_name):
        """Fetches cost per SFT safely, returns 0 if not found."""
        cost_series = df2[(df2['MONTH'] == month) & (df2['PROCESS'] == process_name)]['COST PER SFT']
        return cost_series.sum() if not cost_series.empty else 0

    polish_price = polishing_qty * get_cost("POLISHING")
    grinding_price = grinding_qty * get_cost("GRINDING")
    leather_honed_price = leather_honed_qty * get_cost("LEATHER AND HONED")
    # print("polishing_price",polish_price,grinding_price,leather_honed_price)

    return round(polish_price + grinding_price + leather_honed_price,0)
def epoxy_value(block, df1, df2, month):
    dff1 = df1[df1['BLOCK NO'].str.contains(fr'^{block}\s*[A-Z]?$', na=False, regex=True)]
    epoxy_cost = dff1["COST"].sum()
    
    nettingqty = dff1[dff1["TYPE OF EPOXY"] == 1204]['SLAB SFT'].sum()  # Ensure sum() for scalar value
    netting_price_series = df2[(df2['MONTH'] == month) & (df2['PROCESS'] == "NETTING")]['COST PER SFT']
    # print(netting_price_series)
    
    if not netting_price_series.empty:
        netting_price = nettingqty * netting_price_series.values[0]  # Extract scalar value before multiplication
    else:
        netting_price = 0  # Default to zero if no cost found
    # print("this is the epoxy value",nettingqty,netting_price,epoxy_cost)
    
    return round(epoxy_cost + netting_price,0)

def purchase_cost(recovery_df,block_no):
    
    match = re.search(r'\d+', block_no)
    block=match.group()
    # print("this this the block most probabily the number one","\n",block)
    filtered_df = recovery_df[recovery_df['BLOCK NO'].str.contains(rf'^{block}(?:[-\s]?[A-Za-z0-9]+)?$', na=False)]
    # print("This is the filtered Dataframe ",'\n',filtered_df)
    columns_to_convert = [
    "INV AMOUNT WITHOUT GST",
    "SLABS",
    "AMOUNT",
    "TRANSPORT CHARGES PER BLOCK",
    "BALANCE SLABS"]
    filtered_df.loc[:, columns_to_convert] = filtered_df[columns_to_convert].apply(
    lambda x: pd.to_numeric(x, errors='coerce').fillna(0))
    sums=filtered_df[
    columns_to_convert
].sum(axis=0)
    # print(sums)
    # print(filtered_df[columns_to_convert])
    
    return tuple(sums)
    
    
    


