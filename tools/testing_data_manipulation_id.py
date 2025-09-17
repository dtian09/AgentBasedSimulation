#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Testing Data Manipulation Script

This script performs various data manipulations for network testing:
1. For synthetic agent data:
   - Reads in data_synth20_03_2025_v2.csv
   - Analyzes agent IDs for uniqueness and repetition
   - Creates unique agent IDs for each row
   - Saves as data_synth_network_testing.csv

2. For network edge list:
   - Analyzes network statistics from edgeList_46.csv
   - Modifies specific IDs in the edge list
   - Recalculates network statistics
   - Saves as edgeList_46_network_testing.csv
"""

import pandas as pd
import numpy as np
import os
import networkx as nx
from collections import Counter
from tabulate import tabulate
import datetime

def setup_logger():
    """
    Set up a logger to write output to both terminal and a text file.
    Returns the log file handle.
    """
    # Create output directory if it doesn't exist
    log_dir = "/home/shang/smoking/smokingABM/output/network_data_manipulation_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a timestamped log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = f"{log_dir}/network_data_manipulation_log_{timestamp}.txt"
    log_file = open(log_file_path, "w")
    
    print(f"Log file created at: {log_file_path}")
    log_file.write(f"Network Testing Data Manipulation Log - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    return log_file

def write_log(log_file, message, print_to_terminal=True):
    """
    Write a message to both the log file and terminal.
    
    Args:
        log_file: File handle for the log file
        message: Message to write
        print_to_terminal: Whether to also print to terminal (default: True)
    """
    if print_to_terminal:
        print(message)
    log_file.write(message + "\n")

def print_separator(log_file):
    """Print a separator line for better output readability."""
    separator = "-" * 80
    write_log(log_file, separator)

def analyze_agent_data(log_file):
    """
    Analyze the agent data CSV file.
    - Check total rows
    - Check unique and repetitive agent IDs
    - Create unique agent IDs
    - Save as new file
    """
    print_separator(log_file)
    write_log(log_file, "ANALYZING AGENT DATA FILE")
    print_separator(log_file)
    
    # File paths
    input_file = "/home/shang/smoking/smokingABM/data/data_synth20_03_2025_v2.csv"
    output_file = "/home/shang/smoking/smokingABM/data/data_synth_network_testing.csv"
    
    # Read the CSV file
    write_log(log_file, f"Reading file: {input_file}")
    df = pd.read_csv(input_file)
    
    # 1. Check total rows
    total_rows = len(df)
    write_log(log_file, f"Total rows in file: {total_rows}")
    
    # 2. Check unique and repetitive agent IDs BEFORE modification
    agent_ids = df['agentID'].values
    unique_ids = len(set(agent_ids))
    repetitive_ids = total_rows - unique_ids
    
    # Create a summary table for BEFORE modification
    summary_table_before = [
        ["Total Rows", total_rows],
        ["Unique Agent IDs", unique_ids],
        ["Repetitive Agent IDs", repetitive_ids]
    ]
    write_log(log_file, "\nAgent ID Summary BEFORE ID Modification:")
    write_log(log_file, tabulate(summary_table_before, headers=["Metric", "Count"], tablefmt="grid"))
    
    # Get counts by year for more detailed analysis BEFORE modification
    years = sorted(df['year'].unique())
    
    # Analyze repetitive agent IDs specifically from 2011
    write_log(log_file, "\nAnalyzing repetitive agent IDs from 2011:")
    
    # Get IDs from 2011 within range 1-10000
    df_2011 = df[df['year'] == 2011]
    ids_2011 = set(df_2011['agentID'].values)
    ids_2011_filtered = {id for id in ids_2011 if 1 <= id <= 10000}
    
    # Count how many times these IDs appear in other years
    repetitive_from_2011 = {}
    repetitive_counts = Counter()
    
    for year in years:
        if year == 2011:
            continue
            
        df_year = df[df['year'] == year]
        ids_year = set(df_year['agentID'].values)
        
        # Find ids that appear in both 2011 and this year
        common_ids = ids_2011_filtered.intersection(ids_year)
        
        if common_ids:
            repetitive_from_2011[year] = common_ids
            for id in common_ids:
                repetitive_counts[id] += 1
    
    # Create a summary of repetitive IDs from 2011
    year_repetition_table = []
    for year in sorted(repetitive_from_2011.keys()):
        year_total = len(df[df['year'] == year])
        year_repetition_table.append([
            year,
            year_total,
            len(repetitive_from_2011[year])
        ])
    
    if year_repetition_table:
        write_log(log_file, "\nRepetition of 2011 agent IDs (1-10000) in subsequent years:")
        write_log(log_file, tabulate(
            year_repetition_table, 
            headers=["Year", "Total Agents", "Number of 2011 IDs repeated"], 
            tablefmt="grid"
        ))
        
        # Log the most frequently repeated IDs
        top_repeated = repetitive_counts.most_common(20)
        if top_repeated:
            top_repeated_table = [[id, count] for id, count in top_repeated]
            write_log(log_file, "\nTop 20 most frequently repeated agent IDs from 2011:")
            write_log(log_file, tabulate(
                top_repeated_table, 
                headers=["Agent ID", "Number of years repeated"], 
                tablefmt="grid"
            ))
    else:
        write_log(log_file, "No repetitive agent IDs from 2011 found in other years.")
    
    # 3. Create unique IDs for each row
    write_log(log_file, "\nCreating unique IDs for each row.")
    df['agentID'] = np.arange(1, total_rows + 1)
    
    # 4. Check unique and repetitive agent IDs AFTER modification
    agent_ids_after = df['agentID'].values
    unique_ids_after = len(set(agent_ids_after))
    repetitive_ids_after = total_rows - unique_ids_after
    
    # After ID modification, create a summary table
    summary_table_after = [
        ["Total Rows", total_rows],
        ["Unique Agent IDs", unique_ids_after],
        ["Repetitive Agent IDs", repetitive_ids_after]
    ]
    write_log(log_file, "\nAgent ID Summary AFTER ID Modification:")
    write_log(log_file, tabulate(summary_table_after, headers=["Metric", "Count"], tablefmt="grid"))
    
    # Analyze repetitive agent IDs specifically from 2011 AFTER modification
    write_log(log_file, "\nAnalyzing repetitive agent IDs from 2011 AFTER ID Modification:")
    
    # Get IDs from 2011 within range 1-10000 after modification
    df_2011_after = df[df['year'] == 2011]
    ids_2011_after = set(df_2011_after['agentID'].values)
    ids_2011_filtered_after = {id for id in ids_2011_after if 1 <= id <= 10000}
    
    # Count how many times these IDs appear in other years after modification
    repetitive_from_2011_after = {}
    repetitive_counts_after = Counter()
    
    for year in years:
        if year == 2011:
            continue
            
        df_year = df[df['year'] == year]
        ids_year = set(df_year['agentID'].values)
        
        # Find ids that appear in both 2011 and this year
        common_ids = ids_2011_filtered_after.intersection(ids_year)
        
        if common_ids:
            repetitive_from_2011_after[year] = common_ids
            for id in common_ids:
                repetitive_counts_after[id] += 1
    
    # Get counts by year for more detailed analysis AFTER modification
    write_log(log_file, "\nAgents by Year AFTER ID Modification (2011 ID Repetition):")

    # Create year-wise table for AFTER modification showing only Year, Total Agents, and Number of 2011 IDs repeated
    year_table_after = []
    for year in years:
        if year == 2011:
            continue
        year_total = len(df[df['year'] == year])
        repeated_count = len(repetitive_from_2011_after.get(year, set()))
        year_table_after.append([year, year_total, repeated_count])

    write_log(log_file, tabulate(
        year_table_after, 
        headers=["Year", "Total Agents", "Number of 2011 IDs repeated"], 
        tablefmt="grid"
    ))
    
    # Create a comparison table showing before and after repetition counts
    if any(repetitive_from_2011.values()) or any(repetitive_from_2011_after.values()):
        comparison_table = []
        for year in sorted(set(repetitive_from_2011.keys()) | set(repetitive_from_2011_after.keys())):
            before_count = len(repetitive_from_2011.get(year, set()))
            after_count = len(repetitive_from_2011_after.get(year, set()))
            difference = after_count - before_count
            comparison_table.append([year, before_count, after_count, difference])
        
        write_log(log_file, "\nComparison of 2011 ID Repetition (Before vs After Modification):")
        write_log(log_file, tabulate(
            comparison_table,
            headers=["Year", "IDs Repeated (Before)", "IDs Repeated (After)", "Difference"],
            tablefmt="grid"
        ))
        
        # Show some of the top repeated IDs after modification if any exist
        top_repeated_after = repetitive_counts_after.most_common(20)
        if top_repeated_after:
            top_repeated_table = [[id, count] for id, count in top_repeated_after]
            write_log(log_file, "\nTop 20 most frequently repeated agent IDs from 2011 AFTER modification:")
            write_log(log_file, tabulate(
                top_repeated_table, 
                headers=["Agent ID", "Number of years repeated"], 
                tablefmt="grid"
            ))
    else:
        write_log(log_file, "No repetitive agent IDs from 2011 found in other years after modification.")
    
    # Analyze and report demographic distributions
    write_log(log_file, "\nAnalyzing demographic distributions for PAge and PGender:")
    
    # PAge distribution
    if 'pAge' in df.columns:
        page_counts = df['pAge'].value_counts().sort_index()
        page_table = [[age, count, round(count / len(df) * 100, 2)] 
                      for age, count in page_counts.items()]
        
        write_log(log_file, "\nPAge Distribution:")
        write_log(log_file, tabulate(
            page_table, 
            headers=["Age", "Count", "Percentage (%)"], 
            tablefmt="grid"
        ))
    else:
        write_log(log_file, "No pAge column found in the dataset.")
    
    # PGender distribution
    if 'pGender' in df.columns:
        gender_counts = df['pGender'].value_counts()
        gender_table = [[gender, count, round(count / len(df) * 100, 2)] 
                        for gender, count in gender_counts.items()]
        
        write_log(log_file, "\nPGender Distribution:")
        write_log(log_file, tabulate(
            gender_table, 
            headers=["Gender", "Count", "Percentage (%)"], 
            tablefmt="grid"
        ))
    else:
        write_log(log_file, "No pGender column found in the dataset.")
    
    # 5. Save the new file
    write_log(log_file, f"\nSaving new file to: {output_file}")
    df.to_csv(output_file, index=False)
    
    write_log(log_file, f"Successfully saved file with {total_rows} uniquely identified agents.")
    return total_rows, df  # Return the total number of agents and the modified dataframe for network analysis

def analyze_network_data(num_agents, agent_df, log_file):
    """
    Analyze the network data CSV file.
    - Calculate network statistics
    - Modify IDs for specific nodes
    - Recalculate statistics
    - Save as new file
    
    Args:
        num_agents (int): Total number of agents from the agent data file
        agent_df (DataFrame): The agent dataframe with modified IDs
        log_file: File handle for the log file
    """
    print_separator(log_file)
    write_log(log_file, "ANALYZING NETWORK DATA FILE")
    print_separator(log_file)
    
    # File paths
    input_file = "/home/shang/smoking/smokingABM/data/calibrated_network/edgeList_46.csv"
    output_file = "/home/shang/smoking/smokingABM/data/calibrated_network/edgeList_46_network_testing.csv"
    
    # Read the CSV file
    write_log(log_file, f"Reading file: {input_file}")
    df = pd.read_csv(input_file)
    
    # 1. Create network from edge list ONLY (no isolates added)
    G_edges_only = nx.DiGraph()
    
    # Add edges (nodes will be added automatically)
    for _, row in df.iterrows():
        G_edges_only.add_edge(row['ego.id'], row['alter.id'])
    
    # Calculate network statistics (edges only)
    total_nodes_edges_only = G_edges_only.number_of_nodes()
    total_edges = G_edges_only.number_of_edges()
    
    # Calculate average out-degree (no isolates by definition since we only added edges)
    out_degrees = [G_edges_only.out_degree(n) for n in G_edges_only.nodes()]
    avg_out_degree = sum(out_degrees) / total_nodes_edges_only if total_nodes_edges_only > 0 else 0
    
    # Calculate reciprocity
    reciprocity = nx.reciprocity(G_edges_only) if total_edges > 0 else 0
    
    # 2. Create a second graph with all possible agents as nodes
    G_with_isolates = nx.DiGraph()
    
    # Add all agent IDs as nodes
    all_agent_ids = set(agent_df['agentID'].values)
    G_with_isolates.add_nodes_from(all_agent_ids)
    
    # Add the same edges as before
    for _, row in df.iterrows():
        G_with_isolates.add_edge(row['ego.id'], row['alter.id'])
    
    # Calculate network statistics with isolates
    total_nodes_with_isolates = G_with_isolates.number_of_nodes()
    
    # Find isolated nodes
    isolates = list(nx.isolates(G_with_isolates))
    num_isolates = len(isolates)
    
    # Calculate average out-degree including isolates
    out_degrees_with_isolates = [G_with_isolates.out_degree(n) for n in G_with_isolates.nodes()]
    avg_out_degree_with_isolates = sum(out_degrees_with_isolates) / total_nodes_with_isolates if total_nodes_with_isolates > 0 else 0
    
    # Print network statistics as tables
    edges_only_stats = [
        ["Total nodes (in edge list)", total_nodes_edges_only],
        ["Total edges", total_edges],
        ["Average out-degree", f"{avg_out_degree:.4f}"],
        ["Reciprocity", f"{reciprocity:.4f}"]
    ]
    
    with_isolates_stats = [
        ["Total nodes (all agents)", total_nodes_with_isolates],
        ["Nodes in edge list", total_nodes_edges_only],
        ["Nodes missing from edge list", total_nodes_with_isolates - total_nodes_edges_only],
        ["Total edges", total_edges],
        ["Number of isolates", num_isolates],
        ["Average out-degree (with isolates)", f"{avg_out_degree_with_isolates:.4f}"],
        ["Average out-degree (edge list only)", f"{avg_out_degree:.4f}"],
        ["Reciprocity", f"{reciprocity:.4f}"]
    ]
    
    write_log(log_file, "\nNetwork Statistics (Edge List Only):")
    write_log(log_file, tabulate(edges_only_stats, headers=["Metric", "Value"], tablefmt="grid"))
    
    write_log(log_file, "\nNetwork Statistics (With All Potential Agents):")
    write_log(log_file, tabulate(with_isolates_stats, headers=["Metric", "Value"], tablefmt="grid"))
    
    # Analyze homophily in the network
    write_log(log_file, "\nAnalyzing homophily in the network:")
    
    # Create node attributes dictionary for PAge and PGender
    if 'pAge' in agent_df.columns and 'pGender' in agent_df.columns:
        # Create dictionaries mapping agent IDs to attributes
        page_dict = agent_df.set_index('agentID')['pAge'].to_dict()
        pgender_dict = agent_df.set_index('agentID')['pGender'].to_dict()
        
        # Only keep nodes that are in the network
        network_nodes = set(G_edges_only.nodes())
        page_dict = {k: v for k, v in page_dict.items() if k in network_nodes}
        pgender_dict = {k: v for k, v in pgender_dict.items() if k in network_nodes}
        
        # Set node attributes
        nx.set_node_attributes(G_edges_only, page_dict, 'pAge')
        nx.set_node_attributes(G_edges_only, pgender_dict, 'pGender')
        
        # Calculate homophily using assortativity
        try:
            # Age assortativity (numeric)
            age_assortativity = nx.numeric_assortativity_coefficient(G_edges_only, 'pAge')
            
            # Gender assortativity (categorical)
            gender_assortativity = nx.attribute_assortativity_coefficient(G_edges_only, 'pGender')
            
            homophily_stats = [
                ["Age Assortativity", f"{age_assortativity:.4f}"],
                ["Gender Assortativity", f"{gender_assortativity:.4f}"]
            ]
            
            write_log(log_file, "\nHomophily Measures:")
            write_log(log_file, tabulate(homophily_stats, headers=["Measure", "Value"], tablefmt="grid"))
            
            # Calculate edge distribution by PAge and PGender
            write_log(log_file, "\nEdge Distribution by Demographics:")
            
            # For each edge, get attributes of both nodes
            edge_demo_counts = {
                'same_gender': 0,
                'diff_gender': 0,
                'same_age': 0,
                'age_diff_1_5': 0,
                'age_diff_6_10': 0,
                'age_diff_gt_10': 0,
                'total_edges': 0
            }
            
            for u, v in G_edges_only.edges():
                edge_demo_counts['total_edges'] += 1
                
                # Check gender homophily
                if u in pgender_dict and v in pgender_dict:
                    if pgender_dict[u] == pgender_dict[v]:
                        edge_demo_counts['same_gender'] += 1
                    else:
                        edge_demo_counts['diff_gender'] += 1
                
                # Check age homophily
                if u in page_dict and v in page_dict:
                    age_diff = abs(page_dict[u] - page_dict[v])
                    if age_diff == 0:
                        edge_demo_counts['same_age'] += 1
                    elif 1 <= age_diff <= 5:
                        edge_demo_counts['age_diff_1_5'] += 1
                    elif 6 <= age_diff <= 10:
                        edge_demo_counts['age_diff_6_10'] += 1
                    else:
                        edge_demo_counts['age_diff_gt_10'] += 1
            
            # Create table of edge demographics
            edge_demo_table = []
            for key in ['same_gender', 'diff_gender', 'same_age', 'age_diff_1_5', 'age_diff_6_10', 'age_diff_gt_10']:
                count = edge_demo_counts[key]
                percentage = round(count / edge_demo_counts['total_edges'] * 100, 2) if edge_demo_counts['total_edges'] > 0 else 0
                edge_demo_table.append([key, count, percentage])
            
            write_log(log_file, "\nEdge Demographics:")
            write_log(log_file, tabulate(
                edge_demo_table, 
                headers=["Category", "Count", "Percentage (%)"], 
                tablefmt="grid"
            ))
            
        except Exception as e:
            write_log(log_file, f"Error calculating homophily: {str(e)}")
    else:
        write_log(log_file, "Cannot analyze homophily: missing pAge or pGender columns in agent data.")
    
    # 3. Modify IDs for specific nodes (1-100)
    write_log(log_file, "\nModifying node IDs (1-100):")
    
    # Create mapping for IDs 1-100 (if they exist)
    all_ids = set(df['ego.id'].tolist() + df['alter.id'].tolist())
    id_mapping = {}
    for old_id in range(1, 101):
        if old_id in all_ids:
            id_mapping[old_id] = 10000 + old_id
    
    # Log the mapping of changed IDs
    if id_mapping:
        write_log(log_file, "\nID Mapping (old ID → new ID):")
        id_mapping_table = [[old_id, new_id] for old_id, new_id in id_mapping.items()]
        write_log(log_file, tabulate(id_mapping_table, headers=["Original ID", "New ID"], tablefmt="grid"))
    else:
        write_log(log_file, "\nNo IDs found in the range 1-100 to modify.")
    
    # Apply mapping to edge list dataframe
    new_df = df.copy()
    
    # Replace IDs in both ego.id and alter.id columns
    changed_edges = []
    for old_id, new_id in id_mapping.items():
        # Find edges with old_id before changing them
        ego_edges = new_df[new_df['ego.id'] == old_id]
        alter_edges = new_df[new_df['alter.id'] == old_id]
        
        # Track changes for logging
        for _, row in ego_edges.iterrows():
            changed_edges.append({
                'type': 'ego',
                'old_id': old_id,
                'new_id': new_id,
                'edge': f"{old_id} → {row['alter.id']}",
                'new_edge': f"{new_id} → {row['alter.id']}"
            })
        
        for _, row in alter_edges.iterrows():
            changed_edges.append({
                'type': 'alter',
                'old_id': old_id,
                'new_id': new_id,
                'edge': f"{row['ego.id']} → {old_id}",
                'new_edge': f"{row['ego.id']} → {new_id}"
            })
        
        # Perform the actual replacement
        new_df.loc[new_df['ego.id'] == old_id, 'ego.id'] = new_id
        new_df.loc[new_df['alter.id'] == old_id, 'alter.id'] = new_id
    
    # Log the changed edges
    if changed_edges:
        write_log(log_file, f"\nNodes Modified: {len(id_mapping)} - Edges Modified: {len(changed_edges)}")
        # Display a sample of changed edges (first 20)
        sample_size = min(20, len(changed_edges))
        edge_change_table = [[
            i+1,
            change['edge'],
            change['new_edge'],
            change['type'],
            change['old_id'],
            change['new_id']
        ] for i, change in enumerate(changed_edges[:sample_size])]
        
        write_log(log_file, "\nSample of Modified Edges (first 20):")
        write_log(log_file, tabulate(
            edge_change_table, 
            headers=["#", "Original Edge", "New Edge", "Type", "Old ID", "New ID"], 
            tablefmt="grid"
        ))
        
        if len(changed_edges) > 20:
            write_log(log_file, f"... and {len(changed_edges) - 20} more changes.")
    
    # 4. Create new networks with modified edges
    # Edge list only
    G_new_edges_only = nx.DiGraph()
    
    # Add edges (nodes will be added automatically)
    for _, row in new_df.iterrows():
        G_new_edges_only.add_edge(row['ego.id'], row['alter.id'])
    
    # Calculate network statistics (edges only) after modification
    total_nodes_new_edges_only = G_new_edges_only.number_of_nodes()
    total_edges_new = G_new_edges_only.number_of_edges()
    
    # Calculate average out-degree (no isolates by definition)
    out_degrees_new = [G_new_edges_only.out_degree(n) for n in G_new_edges_only.nodes()]
    avg_out_degree_new = sum(out_degrees_new) / total_nodes_new_edges_only if total_nodes_new_edges_only > 0 else 0
    
    # Calculate reciprocity
    reciprocity_new = nx.reciprocity(G_new_edges_only) if total_edges_new > 0 else 0
    
    # Create comparison table
    comparison_stats = [
        ["Total nodes (in edge list)", total_nodes_edges_only, total_nodes_new_edges_only, total_nodes_new_edges_only - total_nodes_edges_only],
        ["Total edges", total_edges, total_edges_new, total_edges_new - total_edges],
        ["Average out-degree", f"{avg_out_degree:.4f}", f"{avg_out_degree_new:.4f}", f"{avg_out_degree_new - avg_out_degree:.4f}"],
        ["Reciprocity", f"{reciprocity:.4f}", f"{reciprocity_new:.4f}", f"{reciprocity_new - reciprocity:.4f}"]
    ]
    
    write_log(log_file, "\nNetwork Statistics Comparison (Edge List Only):")
    write_log(log_file, tabulate(
        comparison_stats, 
        headers=["Metric", "Original", "Modified", "Difference"], 
        tablefmt="grid"
    ))
    
    # Build new network with all potential agents using modified edge list (new_df)
    G_new_with_isolates = nx.DiGraph()
    G_new_with_isolates.add_nodes_from(set(agent_df['agentID'].values))
    for _, row in new_df.iterrows():
        G_new_with_isolates.add_edge(row['ego.id'], row['alter.id'])
    total_nodes_new_with_isolates = G_new_with_isolates.number_of_nodes()
    total_edges_new_with_isolates = G_new_with_isolates.number_of_edges()
    isolates_new = list(nx.isolates(G_new_with_isolates))
    num_isolates_new = len(isolates_new)
    out_degrees_new_with_isolates = [G_new_with_isolates.out_degree(n) for n in G_new_with_isolates.nodes()]
    avg_out_degree_new_with_isolates = sum(out_degrees_new_with_isolates) / total_nodes_new_with_isolates if total_nodes_new_with_isolates > 0 else 0
    reciprocity_new_with_isolates = nx.reciprocity(G_new_with_isolates) if total_edges_new_with_isolates > 0 else 0

    comparison_stats_with = [
        ["Total nodes (all agents)", total_nodes_with_isolates, total_nodes_new_with_isolates, total_nodes_new_with_isolates - total_nodes_with_isolates],
        ["Nodes missing from edge list", total_nodes_with_isolates - total_nodes_edges_only, total_nodes_new_with_isolates - total_nodes_new_edges_only, (total_nodes_new_with_isolates - total_nodes_new_edges_only) - (total_nodes_with_isolates - total_nodes_edges_only)],
        ["Total edges", total_edges, total_edges_new_with_isolates, total_edges_new_with_isolates - total_edges],
        ["Number of isolates", num_isolates, num_isolates_new, num_isolates_new - num_isolates],
        ["Average out-degree (with isolates)", f"{avg_out_degree_with_isolates:.4f}", f"{avg_out_degree_new_with_isolates:.4f}", f"{avg_out_degree_new_with_isolates - avg_out_degree_with_isolates:.4f}"],
        ["Reciprocity", f"{reciprocity:.4f}", f"{reciprocity_new_with_isolates:.4f}", f"{reciprocity_new_with_isolates - reciprocity:.4f}"]
    ]
    write_log(log_file, "\nNetwork Statistics Comparison (With All Potential Agents):")
    write_log(log_file, tabulate(comparison_stats_with, headers=["Metric", "Original", "Modified", "Difference"], tablefmt="grid"))

    # Continue with saving the modified edge list
    write_log(log_file, f"\nSaving modified edge list to: {output_file}")
    new_df.to_csv(output_file, index=False)
    
    write_log(log_file, f"Successfully saved file with modified node IDs.")

def main():
    """Main function to run all data manipulation tasks."""
    # Set up logger
    log_file = setup_logger()
    
    try:
        write_log(log_file, "Starting data manipulation tasks for network testing.")
        
        # 1. Analyze agent data and get total number of agents and modified dataframe
        num_agents, agent_df = analyze_agent_data(log_file)
        
        # 2. Analyze and modify network data
        analyze_network_data(num_agents, agent_df, log_file)
        
        print_separator(log_file)
        write_log(log_file, "All data manipulation tasks completed successfully.")
        print_separator(log_file)
    
    except Exception as e:
        write_log(log_file, f"ERROR: An exception occurred: {str(e)}")
        import traceback
        write_log(log_file, traceback.format_exc())
    
    finally:
        # Close the log file
        log_file.close()

if __name__ == "__main__":
    main() 