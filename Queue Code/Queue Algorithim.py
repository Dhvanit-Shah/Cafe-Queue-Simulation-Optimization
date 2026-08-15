import pandas as pd
from datetime import datetime, timedelta

DATA_FILE = "Cafe_Queue_Simulator.xlsx"
MAX_WAIT_MINUTES = 8.0  # Threshold to prevent queue starvation


def calculate_prep_time(items_str, menu_lookup):
   # Calculates total preparation time for comma separated item IDs.
    if pd.isna(items_str):
        return 0.0
    
    item_ids = [item.strip() for item in str(items_str).split(',')]
    return sum(menu_lookup.get(item, 0.0) for item in item_ids)


def run_fcfs(df):
    # Simulates First-Come, First-Served queue processing.
    start_times, end_times, wait_times = [], [], []
    worker_free_at = df['Arrival_dt'].iloc[0]

    for _, row in df.iterrows():
        arrival = row['Arrival_dt']
        prep = row['Total_Prep_Time']

        start = max(arrival, worker_free_at)
        end = start + timedelta(minutes=prep)
        wait = (start - arrival).total_seconds() / 60.0

        start_times.append(start.strftime('%H:%M:%S'))
        end_times.append(end.strftime('%H:%M:%S'))
        wait_times.append(round(wait, 2))

        worker_free_at = end

    df['FCFS_Start'] = start_times
    df['FCFS_End'] = end_times
    df['FCFS_Wait_Min'] = wait_times
    return df


def run_spt_fairness(df, wait_threshold=MAX_WAIT_MINUTES):
    # Simulates Shortest Processing Time priority with a wait-time override.
    remaining = df.copy()
    current_time = remaining['Arrival_dt'].iloc[0]

    results = {}

    while not remaining.empty:
        # Get orders that have arrived by current_time
        available = remaining[remaining['Arrival_dt'] <= current_time]

        # Handle idle gaps in arrivals
        if available.empty:
            current_time = remaining['Arrival_dt'].min()
            available = remaining[remaining['Arrival_dt'] <= current_time]

        # Calculate current wait times for available orders
        waits = (current_time - available['Arrival_dt']).dt.total_seconds() / 60.0
        overdue = available[waits >= wait_threshold]

        if not overdue.empty:
            # Override SPT: pick the order waiting the longest
            next_idx = waits.idxmax()
            next_order = available.loc[next_idx]
        else:
            # Pick shortest prep time
            next_order = available.sort_values(by='Total_Prep_Time').iloc[0]

        order_id = next_order['Order_ID']
        arrival = next_order['Arrival_dt']
        prep = next_order['Total_Prep_Time']

        start = current_time
        end = start + timedelta(minutes=prep)
        wait = (start - arrival).total_seconds() / 60.0

        results[order_id] = {
            'Opt_Start': start.strftime('%H:%M:%S'),
            'Opt_End': end.strftime('%H:%M:%S'),
            'Opt_Wait_Min': round(wait, 2)
        }

        current_time = end
        remaining = remaining[remaining['Order_ID'] != order_id]

    res_df = pd.DataFrame.from_dict(results, orient='index')
    return df.merge(res_df, left_on='Order_ID', right_index=True)


def main():
    # Load data
    menu_df = pd.read_excel(DATA_FILE, sheet_name="Menu_Dictionary")
    orders_df = pd.read_excel(DATA_FILE, sheet_name="Order_Log")

    # Map menu pricing/times
    menu_dict = dict(zip(menu_df['Item_ID'].str.strip(), menu_df['Prep_Time_Minutes']))
    orders_df['Total_Prep_Time'] = orders_df['Item_IDs'].apply(
        lambda x: calculate_prep_time(x, menu_dict)
    )

    # Parse timestamps
    today_str = datetime.today().strftime('%Y-%m-%d')
    orders_df['Arrival_dt'] = pd.to_datetime(today_str + ' ' + orders_df['Arrival_Time'].astype(str))

    # Run simulations
    orders_df = run_fcfs(orders_df)
    orders_df = run_spt_fairness(orders_df)

    # Display summary
    print("--- Queue Performance Metrics ---")
    print(f"FCFS Avg Wait: {orders_df['FCFS_Wait_Min'].mean():.2f} mins")
    print(f"Optimized Avg Wait: {orders_df['Opt_Wait_Min'].mean():.2f} mins")

    # Export
    orders_df.to_excel("Simulation_Results.xlsx", index=False)
    print("Saved results to Simulation_Results.xlsx")


if __name__ == "__main__":
    main()