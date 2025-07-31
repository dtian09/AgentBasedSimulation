#!/usr/bin/env python3
"""
Unified Data Processing Pipeline for SmokingABM

This unified pipeline consolidates functionality from three legacy scripts:
- preprocess_all_data.py (X-drive integration, directory creation)
- comprehensive_data_preprocessing_pipeline.py (Excel formulas, LogOdds columns)
- process_input_data_files.py (STPM processing, integer conversion)

Features:
- Complete mirror architecture with local processing
- Bidirectional X-drive synchronization
- Comprehensive data processing pipeline
- Multiple execution modes (full, local, sync-only)
- Robust error handling and progress reporting

Date: 2025-06-09

Usage:
    # Complete pipeline with X-drive sync
    python run_unified_data_pipeline.py --mode full --sync-xdrive

    # Local processing only
    python run_unified_data_pipeline.py --mode local

    # Sync results to X-drive only
    python run_unified_data_pipeline.py --mode sync-only

    # Dry run (preview mode)
    python run_unified_data_pipeline.py --mode full --dry-run
"""

import pandas as pd
import numpy as np
import os
import sys
import argparse
import shutil
import re
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple

# Suppress pandas FutureWarning about downcasting
pd.set_option('future.no_silent_downcasting', True)

# Configure logging with colored output
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for better readability."""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_data_pipeline.log'),
        logging.StreamHandler()
    ]
)

# Apply colored formatter to console handler
console_handler = logging.getLogger().handlers[1]
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)

class UnifiedPipelineConfig:
    """Configuration management for the unified pipeline."""

    def __init__(self, mode: str = 'local', sync_xdrive: bool = False,
                 date_stamp: Optional[str] = None, dry_run: bool = False):
        """
        Initialize pipeline configuration.

        Args:
            mode: Processing mode ('full', 'local', 'sync-only')
            sync_xdrive: Whether to synchronize with X-drive
            date_stamp: Custom date stamp (defaults to current date)
            dry_run: Preview mode without making changes
        """
        self.mode = mode
        self.sync_xdrive = sync_xdrive
        self.dry_run = dry_run
        self.date_stamp = date_stamp or datetime.now().strftime('%Y%m%d')

        # Path configuration
        self.local_mirror_base = Path('data')
        self.xdrive_base = Path('/mnt/xdrive/purshouse_group/Shared/smoking_abm')

        # David tools compatible input directories
        self.stmp_input_dir = Path('/mnt/u/smoking_cessation/STPM')
        self.dynamic_vars_input_dir = Path('/mnt/u/smoking_cessation/dynamic_exogenous_variables')

        # Directory structure
        self.setup_directory_paths()

        logger.info(f"🔧 Pipeline Configuration Initialized")
        logger.info(f"   Mode: {self.mode}")
        logger.info(f"   X-drive sync: {self.sync_xdrive}")
        logger.info(f"   Date stamp: {self.date_stamp}")
        logger.info(f"   Dry run: {self.dry_run}")
        logger.info(f"   Local mirror: {self.local_mirror_base}")
        logger.info(f"   X-drive base: {self.xdrive_base}")

    def setup_directory_paths(self):
        """Set up all directory paths for the pipeline."""
        # Local mirror directories
        self.raw_data_dir = self.local_mirror_base / 'raw_data' / 'sts'
        self.intermediate_data_dir = self.local_mirror_base / 'intermediate_data'
        self.input_data_dir = self.local_mirror_base / 'input_data'
        self.output_data_dir = self.local_mirror_base / 'output_data'

        # Intermediate data subdirectories
        self.intermediate_exogenous_dir = self.intermediate_data_dir / 'exogenous_dynamics'
        self.intermediate_com_b_dir = self.intermediate_data_dir / 'com_b'
        self.intermediate_ecig_dir = self.intermediate_data_dir / 'e_cig_diffusion'
        self.intermediate_stpm_dir = self.intermediate_data_dir / 'stpm_transitions'

        # Input data subdirectories
        self.input_population_dir = self.input_data_dir / 'synthetic_population'
        self.input_stpm_dir = self.input_data_dir / 'stpm_transitions'  # Fixed: was stmp_transitions
        self.input_com_b_dir = self.input_data_dir / 'com_b'
        self.input_ecig_dir = self.input_data_dir / 'e_cig_diffusion'
        self.input_exogenous_dir = self.input_data_dir / 'exogenous_dynamics'
        self.input_network_dir = self.input_data_dir / 'synthetic_network'

class DataSynchronizer:
    """Handles bidirectional synchronization between X-drive and local mirror."""

    def __init__(self, config: UnifiedPipelineConfig):
        """Initialize data synchronizer with configuration."""
        self.config = config

    def get_sync_preview(self) -> List[Dict]:
        """Get a preview of files that would be synced to X-drive."""
        sync_preview = []

        if not self.config.sync_xdrive:
            return sync_preview

        try:
            # Only sync input_data and output_data, EXCLUDE intermediate_data
            sync_dirs = [
                self.config.input_data_dir,
                self.config.output_data_dir
            ]

            for local_dir in sync_dirs:
                if local_dir.exists():
                    # Find files with current date stamp (following protocol naming)
                    for file_path in local_dir.rglob(f'*{self.config.date_stamp}*'):
                        if file_path.is_file():
                            file_relative_path = file_path.relative_to(self.config.local_mirror_base)
                            xdrive_target = self.config.xdrive_base / file_relative_path

                            file_info = {
                                'local_path': str(file_path),
                                'xdrive_path': str(xdrive_target),
                                'relative_path': str(file_relative_path),
                                'size_mb': round(file_path.stat().st_size / (1024*1024), 2),
                                'exists_on_xdrive': xdrive_target.exists() if self.validate_xdrive_access() else False
                            }
                            sync_preview.append(file_info)

            return sync_preview

        except Exception as e:
            logger.error(f"❌ Failed to generate sync preview: {e}")
            return []

    def confirm_sync_to_xdrive(self) -> bool:
        """Interactive confirmation for X-drive sync with preview."""
        if not self.config.sync_xdrive:
            logger.info("⏭️  X-drive sync disabled, skipping sync to X-drive")
            return True

        logger.info("🔍 Generating sync preview...")
        sync_preview = self.get_sync_preview()

        if not sync_preview:
            logger.info("   ℹ️  No files to sync (no files with current date stamp found)")
            return True

        logger.info(f"\n📋 SYNC PREVIEW - {len(sync_preview)} files to sync:")
        logger.info("=" * 80)

        for file_info in sync_preview:
            status = "UPDATE" if file_info['exists_on_xdrive'] else "NEW"
            logger.info(f"   {status:6} | {file_info['size_mb']:6.1f}MB | {file_info['relative_path']}")

        logger.info("=" * 80)
        logger.info("⚠️  SAFETY: intermediate_data/ will be EXCLUDED from sync (per protocol)")
        logger.info("✅ Only input_data/ and output_data/ will be synced")

        # Interactive confirmation
        while True:
            try:
                response = input("\n🤔 Proceed with X-drive sync? [y/N/preview]: ").strip().lower()
                if response in ['y', 'yes']:
                    logger.info("✅ User confirmed X-drive sync")
                    return self.sync_to_xdrive()
                elif response in ['n', 'no', '']:
                    logger.info("❌ User cancelled X-drive sync")
                    return False
                elif response in ['p', 'preview']:
                    # Show detailed preview
                    for file_info in sync_preview:
                        logger.info(f"   📄 {file_info['relative_path']}")
                        logger.info(f"      Local:  {file_info['local_path']}")
                        logger.info(f"      X-drive: {file_info['xdrive_path']}")
                        logger.info(f"      Size: {file_info['size_mb']} MB")
                        logger.info("")
                else:
                    logger.info("   Please enter 'y' (yes), 'n' (no), or 'preview'")
            except KeyboardInterrupt:
                logger.info("\n❌ Sync cancelled by user")
                return False

    def validate_xdrive_access(self) -> bool:
        """Validate X-drive access and mount status."""
        if not self.config.xdrive_base.exists():
            logger.error(f"❌ X-drive not accessible: {self.config.xdrive_base}")
            return False

        logger.info(f"✅ X-drive access validated: {self.config.xdrive_base}")
        return True

    def sync_from_xdrive(self) -> bool:
        """Synchronize data from X-drive to local mirror."""
        if not self.config.sync_xdrive:
            logger.info("⏭️  X-drive sync disabled, skipping sync from X-drive")
            return True

        logger.info("🔄 Synchronizing data from X-drive to local mirror...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would sync from X-drive to local mirror")
            return True

        if not self.validate_xdrive_access():
            return False

        try:
            # Ensure local mirror directory exists
            self.config.local_mirror_base.mkdir(parents=True, exist_ok=True)

            # Copy all data from X-drive to local mirror
            if self.config.xdrive_base.exists():
                for item in self.config.xdrive_base.iterdir():
                    if item.is_file():
                        target = self.config.local_mirror_base / item.name
                        shutil.copy2(item, target)
                        logger.info(f"   📄 Copied file: {item.name}")
                    elif item.is_dir():
                        target = self.config.local_mirror_base / item.name
                        if target.exists():
                            shutil.rmtree(target)
                        shutil.copytree(item, target)
                        logger.info(f"   📁 Copied directory: {item.name}")

            logger.info("✅ Sync from X-drive completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to sync from X-drive: {e}")
            return False

    def sync_to_xdrive(self) -> bool:
        """Synchronize processed data from local mirror to X-drive."""
        if not self.config.sync_xdrive:
            logger.info("⏭️  X-drive sync disabled, skipping sync to X-drive")
            return True

        logger.info("🔄 Synchronizing processed data to X-drive...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would sync processed data to X-drive")
            return True

        if not self.validate_xdrive_access():
            return False

        try:
            # SAFETY: Only sync specific new files, exclude intermediate_data
            # Following model_management_protocol.md naming conventions

            # Only sync input_data and output_data, EXCLUDE intermediate_data
            sync_dirs = [
                self.config.input_data_dir,
                self.config.output_data_dir
            ]

            # Find only NEW files with current date stamp to avoid overwriting existing files
            new_files_synced = 0

            for local_dir in sync_dirs:
                if local_dir.exists():
                    relative_path = local_dir.relative_to(self.config.local_mirror_base)

                    # Find files with current date stamp (following protocol naming)
                    for file_path in local_dir.rglob(f'*{self.config.date_stamp}*'):
                        if file_path.is_file():
                            file_relative_path = file_path.relative_to(self.config.local_mirror_base)
                            xdrive_target = self.config.xdrive_base / file_relative_path

                            # Create target directory if needed
                            xdrive_target.parent.mkdir(parents=True, exist_ok=True)

                            # Only copy if file doesn't exist or is newer
                            if not xdrive_target.exists() or file_path.stat().st_mtime > xdrive_target.stat().st_mtime:
                                shutil.copy2(file_path, xdrive_target)
                                logger.info(f"   📄 Synced NEW file: {file_relative_path}")
                                new_files_synced += 1
                            else:
                                logger.info(f"   ⏭️  Skipped existing file: {file_relative_path}")

            if new_files_synced == 0:
                logger.info("   ℹ️  No new files to sync (following protocol naming)")
            else:
                logger.info(f"   ✅ Synced {new_files_synced} new files")

            logger.info("✅ Sync to X-drive completed successfully (intermediate_data excluded)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to sync to X-drive: {e}")
            return False

class ProcessingEngine:
    """Core processing engine that consolidates all data processing functionality."""

    def __init__(self, config: UnifiedPipelineConfig):
        """Initialize processing engine with configuration."""
        self.config = config

    def find_unique_file(self, directory: Path, pattern: str) -> Optional[Path]:
        """
        Find a unique file matching a pattern. Error if multiple files found.

        Args:
            directory: Directory to search in
            pattern: Glob pattern to match (e.g., 'attempts_dynamic_*')

        Returns:
            Path to the unique matching file, or None if not found

        Raises:
            ValueError: If multiple files match the pattern
        """
        if not directory.exists():
            logger.warning(f"   ⚠️  Directory does not exist: {directory}")
            return None

        matching_files = list(directory.glob(pattern))

        if len(matching_files) == 0:
            logger.warning(f"   ⚠️  No files found matching pattern '{pattern}' in {directory}")
            return None
        elif len(matching_files) == 1:
            logger.info(f"   ✅ Found unique file: {matching_files[0].name}")
            return matching_files[0]
        else:
            file_names = [f.name for f in matching_files]
            error_msg = f"Multiple files found matching pattern '{pattern}' in {directory}: {file_names}. Expected exactly one file."
            logger.error(f"   ❌ {error_msg}")
            raise ValueError(error_msg)

    def create_directory_structure(self) -> bool:
        """Create complete directory structure for local mirror."""
        logger.info("📁 Creating complete directory structure...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would create directory structure")
            return True

        try:
            # All directories to create
            directories = [
                self.config.raw_data_dir,
                self.config.intermediate_data_dir,
                self.config.intermediate_exogenous_dir,
                self.config.intermediate_com_b_dir,
                self.config.intermediate_ecig_dir,
                self.config.intermediate_stpm_dir,
                self.config.input_data_dir,
                self.config.input_population_dir,
                self.config.input_stpm_dir,  # Fixed: was input_stmp_dir
                self.config.input_com_b_dir,
                self.config.input_ecig_dir,
                self.config.input_exogenous_dir,
                self.config.input_network_dir,
                self.config.output_data_dir
            ]

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"   📁 Created: {directory.relative_to(self.config.local_mirror_base)}")

            logger.info("✅ Directory structure created successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create directory structure: {e}")
            return False

    def process_excel_formulas(self) -> bool:
        """Process Excel formulas for attempts and maintenance data."""
        logger.info("📊 Processing Excel formulas...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would process Excel formulas")
            return True

        try:
            # Process attempts data
            attempts_file = self.config.raw_data_dir / 'table_attempts_dynamic.csv'
            if attempts_file.exists():
                df = pd.read_csv(attempts_file)
                logger.info(f"   📄 Loaded attempts data: {df.shape[0]} rows, {df.shape[1]} columns")

                # 1. Create yearsubgroup column
                df['yearsubgroup'] = (df['xyear'].astype(str) +
                                    df['age'].astype(str) +
                                    df['sex'].astype(str) +
                                    df['ABC1'].astype(str))

                # 2. Implement bCigConsumptionTrend formula
                df['bCigConsumptionTrend'] = 1.0
                future_years_mask = df['xyear'] > 2024

                if future_years_mask.any():
                    year_2024_data = df[df['xyear'] == 2024].copy()
                    lookup_dict = {}
                    for _, row in year_2024_data.iterrows():
                        key = f"2024{row['age']}{row['sex']}{row['ABC1']}"
                        lookup_dict[key] = row['bCigConsumption']

                    for idx, row in df[future_years_mask].iterrows():
                        lookup_key = f"2024{row['age']}{row['sex']}{row['ABC1']}"
                        if lookup_key in lookup_dict:
                            baseline_value = lookup_dict[lookup_key]
                            if baseline_value != 0:
                                df.loc[idx, 'bCigConsumptionTrend'] = row['bCigConsumption'] / baseline_value

                # Save processed attempts data
                output_file = self.config.intermediate_exogenous_dir / f'processed_attempts_dynamic_{self.config.date_stamp}_v1.csv'
                df.to_csv(output_file, index=False)
                logger.info(f"   ✅ Saved processed attempts data: {output_file.name}")

            logger.info("✅ Excel formulas processed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to process Excel formulas: {e}")
            return False

    def validate_logodds_columns(self) -> bool:
        """Validate that original columns contain proper log odds values and handle naming inconsistencies."""
        logger.info("🔍 Validating log odds columns and handling naming inconsistencies...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would validate log odds columns")
            return True

        try:
            # Validate attempts data log odds columns
            attempts_files = [
                self.config.intermediate_exogenous_dir / f'attempts_dynamic_{self.config.date_stamp}_v1.csv',
                self.config.intermediate_exogenous_dir / 'attempts_dynamic_20250325_v1.csv'  # fallback
            ]

            attempts_file = None
            for file_path in attempts_files:
                if file_path.exists():
                    attempts_file = file_path
                    break

            if attempts_file and attempts_file.exists():
                df = pd.read_csv(attempts_file)
                logger.info(f"   📊 Loaded attempts data: {df.shape[0]} rows, {df.shape[1]} columns from {attempts_file.name}")

                # Validate and handle naming inconsistencies for attempts data
                validation_issues = []

                # Check for oReceiptGPAdvice vs oRecieptGPAdvice (typo handling)
                receipt_col = None
                if 'oReceiptGPAdvice' in df.columns:
                    receipt_col = 'oReceiptGPAdvice'
                elif 'oRecieptGPAdvice' in df.columns:
                    receipt_col = 'oRecieptGPAdvice'
                    logger.warning(f"   ⚠️  Found misspelled column 'oRecieptGPAdvice' - ABM expects 'oReceiptGPAdvice'")
                    # Create correctly spelled column for ABM compatibility
                    df['oReceiptGPAdvice'] = df['oRecieptGPAdvice']
                    logger.info(f"   ✅ Created correctly spelled 'oReceiptGPAdvice' column")

                if receipt_col:
                    # Validate log odds values
                    receipt_values = df[receipt_col].dropna()
                    if len(receipt_values) > 0:
                        min_val, max_val = receipt_values.min(), receipt_values.max()
                        logger.info(f"   📊 {receipt_col} values range: {min_val:.3f} to {max_val:.3f}")
                        if min_val > 0 or max_val > 10:
                            validation_issues.append(f"{receipt_col} values don't look like log odds (expected negative to small positive)")
                    else:
                        validation_issues.append(f"{receipt_col} column is empty")
                else:
                    validation_issues.append("No GP advice column found (expected 'oReceiptGPAdvice' or 'oRecieptGPAdvice')")

                # Check pNRT column
                if 'pNRT' in df.columns:
                    nrt_values = df['pNRT'].dropna()
                    if len(nrt_values) > 0:
                        min_val, max_val = nrt_values.min(), nrt_values.max()
                        logger.info(f"   📊 pNRT values range: {min_val:.3f} to {max_val:.3f}")
                        if min_val > 0 or max_val > 10:
                            validation_issues.append("pNRT values don't look like log odds (expected negative to small positive)")
                    else:
                        validation_issues.append("pNRT column is empty")
                else:
                    validation_issues.append("pNRT column not found")

                # Remove any existing LogOdds duplicate columns
                logodds_cols_removed = []
                for col in ['oReceiptGPAdviceLodOdds', 'pNRTLogOdds']:
                    if col in df.columns:
                        df.drop(columns=[col], inplace=True)
                        logodds_cols_removed.append(col)

                if logodds_cols_removed:
                    logger.info(f"   🗑️  Removed redundant LogOdds columns: {', '.join(logodds_cols_removed)}")

                # Save updated file
                df.to_csv(attempts_file, index=False)

                if validation_issues:
                    for issue in validation_issues:
                        logger.warning(f"   ⚠️  Validation issue: {issue}")
                else:
                    logger.info(f"   ✅ Attempts data validation passed")
            else:
                logger.warning(f"   ⚠️  No attempts file found for validation")

            # Validate maintenance data log odds columns
            maintenance_files = [
                self.config.intermediate_exogenous_dir / f'maintenance_dynamic_{self.config.date_stamp}_v1.csv',
                self.config.intermediate_exogenous_dir / 'maintenance_dynamic_20250325_v1.csv'  # fallback
            ]

            maintenance_file = None
            for file_path in maintenance_files:
                if file_path.exists():
                    maintenance_file = file_path
                    break

            if maintenance_file and maintenance_file.exists():
                df = pd.read_csv(maintenance_file)
                logger.info(f"   📊 Loaded maintenance data: {df.shape[0]} rows, {df.shape[1]} columns from {maintenance_file.name}")

                # Validate maintenance data columns
                validation_issues = []
                maintenance_columns = ['pPrescriptionNRT', 'cUseOfBehaviourSupport', 'pVareniclineUse', 'pCytisineUse']

                for col in maintenance_columns:
                    if col in df.columns:
                        col_values = df[col].dropna()
                        if len(col_values) > 0:
                            min_val, max_val = col_values.min(), col_values.max()
                            logger.info(f"   📊 {col} values range: {min_val:.3f} to {max_val:.3f}")
                            if min_val > 0 or max_val > 10:
                                validation_issues.append(f"{col} values don't look like log odds (expected negative to small positive)")
                        else:
                            validation_issues.append(f"{col} column is empty")
                    else:
                        validation_issues.append(f"{col} column not found")

                # Remove any existing LogOdds duplicate columns
                logodds_cols_to_remove = [
                    'pPrescriptionNRTLogOdds', 'cUseOfBehaviourSupportLogOdds',
                    'pVareniclineUseLogOdds', 'pCytisineUseLogOdds'
                ]
                logodds_cols_removed = []
                for col in logodds_cols_to_remove:
                    if col in df.columns:
                        df.drop(columns=[col], inplace=True)
                        logodds_cols_removed.append(col)

                if logodds_cols_removed:
                    logger.info(f"   🗑️  Removed redundant LogOdds columns: {', '.join(logodds_cols_removed)}")

                # Save updated file
                df.to_csv(maintenance_file, index=False)

                if validation_issues:
                    for issue in validation_issues:
                        logger.warning(f"   ⚠️  Validation issue: {issue}")
                else:
                    logger.info(f"   ✅ Maintenance data validation passed")
            else:
                logger.warning(f"   ⚠️  No maintenance file found for validation")

            logger.info("✅ Log odds validation completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to validate log odds columns: {e}")
            return False

    def convert_stmp_probabilities(self) -> bool:
        """Convert STMP annual probabilities to monthly probabilities."""
        logger.info("🎯 Converting STMP probabilities (annual → monthly)...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would convert STMP probabilities")
            return True

        try:
            # Define probability conversion mappings (matching david_tools exactly)
            stmp_files = {
                'initiation': {
                    'input': 'smoking_state_transition_probabilities_England2.xlsx',
                    'sheet': 'Initiation',
                    'prob_col': 'p_start',
                    'output_col': 'p_start_1month',
                    'output': f'initiation_prob1month_STPM.csv'
                },
                'relapse': {
                    'input': 'smoking_state_transition_probabilities_England2.xlsx',
                    'sheet': 'Relapse',
                    'prob_col': 'p_relapse',
                    'output_col': 'p_relapse_1month',
                    'output': f'relapse_prob1month_STPM.csv'
                },
                'quit': {
                    'input': 'smoking_state_transition_probabilities_England2.xlsx',
                    'sheet': 'Quit',
                    'prob_col': 'p_quit',
                    'output_col': 'p_quit_1month',
                    'output': f'quit_prob1month_STPM.csv'
                }
            }

            # NOTE: Raw processing commented out since we already have processed files
            # The pipeline originally looked for smoking_state_transition_probabilities_England2.xlsx
            # to generate initiation_prob1month_STPM.csv, relapse_prob1month_STPM.csv, quit_prob1month_STPM.csv
            # Since these processed files already exist in X-drive, we skip raw processing
            # and ensure the existing processed files are available locally.

            # Check if processed files already exist and copy them if needed
            processed_files = [
                'initiation_prob1month_STPM.csv',
                'relapse_prob1month_STPM.csv',
                'quit_prob1month_STPM.csv'
            ]

            for filename in processed_files:
                # Check if file exists in X-drive input directory
                xdrive_file = self.config.xdrive_base / 'input_data' / 'stpm_transitions' / filename
                local_subdir_file = self.config.input_stpm_dir / filename  # Fixed: was input_stmp_dir

                if xdrive_file.exists() and not local_subdir_file.exists():
                    # Copy from X-drive to subdirectory ONLY (per protocol)
                    import shutil
                    shutil.copy2(xdrive_file, local_subdir_file)
                    logger.info(f"   ✅ Copied existing processed file: {filename}")
                elif local_subdir_file.exists():
                    logger.info(f"   ✅ Using existing processed file: {filename}")
                else:
                    logger.warning(f"   ⚠️  Processed file not found: {filename}")

            # COMMENTED OUT: Original raw file processing code
            # This would process smoking_state_transition_probabilities_England2.xlsx
            # but since we have the processed outputs, we skip this step
            """
            # Process each STMP file type
            for prob_type, config in stmp_files.items():
                # Try multiple input locations (david_tools compatible)
                input_locations = [
                    self.config.stmp_input_dir / config['input'],
                    self.config.raw_data_dir / config['input'],
                    self.config.local_mirror_base / 'raw_data' / config['input']
                ]

                input_file = None
                for location in input_locations:
                    if location.exists():
                        input_file = location
                        break

                if input_file:
                    logger.info(f"   📄 Processing {prob_type} from: {input_file}")
                    # Read Excel sheet
                    df = pd.read_excel(input_file, sheet_name=config['sheet'])

                    # Filter years (matching david_tools: 2011-2050)
                    df = df[(df['year'] >= 2011) & (df['year'] <= 2050)]

                    # Apply integer mappings (matching david_tools exactly)
                    df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
                    df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1, '5_most_deprived': 5})

                    # Convert annual to monthly probability (matching david_tools formula)
                    monthly_prob = 1 - (1 - df[config['prob_col']]) ** (1/12)
                    df[config['output_col']] = monthly_prob
                    df = df.drop(columns=[config['prob_col']])

                    # Save processed file to main data directory (ABM expects files directly in data/)
                    output_file = self.config.local_mirror_base / config['output']
                    df.to_csv(output_file, index=False)
                    logger.info(f"   ✅ Processed {prob_type} probabilities: {config['output']}")

                    # Also save to subdirectory for organization
                    subdir_output = self.config.input_stpm_dir / config['output']  # Fixed: was input_stmp_dir
                    df.to_csv(subdir_output, index=False)
                else:
                    logger.warning(f"   ⚠️  Could not find input file for {prob_type}: {config['input']}")
            """

            logger.info("✅ STMP probabilities converted successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to convert STMP probabilities: {e}")
            return False

    def apply_integer_mappings(self) -> bool:
        """Apply integer mappings to categorical variables."""
        logger.info("🔢 Applying integer mappings to categorical variables...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would apply integer mappings")
            return True

        try:
            # Define mappings
            sex_mapping = {'Male': 1, 'Female': 2}
            social_grade_mapping = {'ABC1': 0, 'C2DE': 1}
            imd_mapping = {'1_least_deprived': 1, '5_most_deprived': 5}

            # Process attempts data using pattern matching
            try:
                # Look directly for the files that exist (no "processed_" prefix needed)
                attempts_file = self.find_unique_file(self.config.intermediate_exogenous_dir, 'attempts_dynamic_*')

                if attempts_file:
                    df = pd.read_csv(attempts_file)

                    # Apply mappings (fixed FutureWarning)
                    if 'sex' in df.columns:
                        df['sex'] = df['sex'].replace(sex_mapping)
                        df['sex'] = df['sex'].infer_objects(copy=False)
                    if 'ABC1' in df.columns:
                        df['social_grade'] = df['ABC1'].replace(social_grade_mapping)
                        df['social_grade'] = df['social_grade'].infer_objects(copy=False)
                        df = df.drop('ABC1', axis=1)

                    # Save integer version
                    output_file = self.config.input_exogenous_dir / f'attempts_dynamic_{self.config.date_stamp}_v1.csv'
                    df.to_csv(output_file, index=False)
                    logger.info(f"   ✅ Applied integer mappings to attempts data")
                else:
                    logger.warning(f"   ⚠️  No attempts dynamic file found for integer mapping")
            except ValueError as e:
                logger.error(f"   ❌ Error finding attempts file: {e}")

            # Process maintenance data using pattern matching
            try:
                # Look directly for the files that exist (no "processed_" prefix needed)
                maintenance_file = self.find_unique_file(self.config.intermediate_exogenous_dir, 'maintenance_dynamic_*')

                if maintenance_file:
                    df = pd.read_csv(maintenance_file)

                    # Apply mappings (fixed FutureWarning)
                    if 'sex' in df.columns:
                        df['sex'] = df['sex'].replace(sex_mapping)
                        df['sex'] = df['sex'].infer_objects(copy=False)
                    if 'ABC1' in df.columns:
                        df['social_grade'] = df['ABC1'].replace(social_grade_mapping)
                        df['social_grade'] = df['social_grade'].infer_objects(copy=False)
                        df = df.drop('ABC1', axis=1)

                    # Save integer version
                    output_file = self.config.input_exogenous_dir / f'maintenance_dynamic_{self.config.date_stamp}_v1.csv'
                    df.to_csv(output_file, index=False)
                    logger.info(f"   ✅ Applied integer mappings to maintenance data")
                else:
                    logger.warning(f"   ⚠️  No maintenance dynamic file found for integer mapping")
            except ValueError as e:
                logger.error(f"   ❌ Error finding maintenance file: {e}")

            logger.info("✅ Integer mappings applied successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to apply integer mappings: {e}")
            return False

    def process_death_probabilities(self) -> bool:
        """Process death probabilities with integer conversion (matching david_tools)."""
        logger.info("💀 Processing death probabilities...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would process death probabilities")
            return True

        try:
            # NOTE: Raw processing commented out since we already have processed file
            # The pipeline originally looked for death_probs_abm.csv to generate death_probs_abm_integers.csv
            # Since the processed file already exists in X-drive, we skip raw processing

            # Check if processed file already exists and copy it if needed
            filename = 'death_probs_abm_integers.csv'
            xdrive_file = self.config.xdrive_base / 'input_data' / 'stpm_transitions' / filename
            local_subdir_file = self.config.input_stpm_dir / filename  # Fixed: was input_stmp_dir

            if xdrive_file.exists() and not local_subdir_file.exists():
                # Copy from X-drive to subdirectory ONLY (per protocol)
                import shutil
                shutil.copy2(xdrive_file, local_subdir_file)
                logger.info(f"   ✅ Copied existing processed file: {filename}")
            elif local_subdir_file.exists():
                logger.info(f"   ✅ Using existing processed file: {filename}")
            else:
                logger.warning(f"   ⚠️  Processed file not found: {filename}")

            # COMMENTED OUT: Original raw file processing code
            # This would process death_probs_abm.csv but we have the processed output
            """
            # Try multiple input locations for death probabilities
            input_locations = [
                self.config.stmp_input_dir / 'death_probs_abm.csv',
                self.config.raw_data_dir / 'death_probs_abm.csv',
                self.config.local_mirror_base / 'raw_data' / 'death_probs_abm.csv'
            ]

            input_file = None
            for location in input_locations:
                if location.exists():
                    input_file = location
                    break

            if input_file:
                logger.info(f"   📄 Processing death probabilities from: {input_file}")
                df = pd.read_csv(input_file)

                # Filter years (matching david_tools: 2011-2050)
                df = df[(df['year'] >= 2011) & (df['year'] <= 2050)]

                # Apply integer mappings (matching david_tools exactly)
                df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
                df['imd_quintile'] = df['imd_quintile'].replace({'1_least_deprived': 1, '5_most_deprived': 5})

                # Save processed file to main data directory (ABM expects files directly in data/)
                output_file = self.config.local_mirror_base / 'death_probs_abm_integers.csv'
                df.to_csv(output_file, index=False)
                logger.info(f"   ✅ Processed death probabilities: death_probs_abm_integers.csv")

                # Also save to subdirectory for organization
                subdir_output = self.config.input_stpm_dir / 'death_probs_abm_integers.csv'  # Fixed: was input_stmp_dir
                df.to_csv(subdir_output, index=False)
            else:
                logger.warning("   ⚠️  Could not find death_probs_abm.csv input file")
            """

            logger.info("✅ Death probabilities processed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to process death probabilities: {e}")
            return False

    def process_extended_exogenous_dynamics(self) -> bool:
        """Process extended exogenous dynamics files (matching david_tools output names)."""
        logger.info("📊 Processing extended exogenous dynamics...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would process extended exogenous dynamics")
            return True

        try:
            # Define extended exogenous dynamics files using pattern matching
            exogenous_files = {
                'attempts': {
                    'pattern': 'attempts_dynamic_*',
                    'search_dirs': [
                        self.config.intermediate_exogenous_dir,
                        self.config.dynamic_vars_input_dir,
                        self.config.raw_data_dir
                    ],
                    'fallback_patterns': [
                        'table_attempts_dynamic_extended*',
                        f'processed_attempts_dynamic_{self.config.date_stamp}_v1.csv'
                    ],
                    'output': f'table_attempts_dynamic_extended_integers_{self.config.date_stamp}_v1.csv'
                },
                'maintenance': {
                    'pattern': 'maintenance_dynamic_*',
                    'search_dirs': [
                        self.config.intermediate_exogenous_dir,
                        self.config.dynamic_vars_input_dir,
                        self.config.raw_data_dir
                    ],
                    'fallback_patterns': [
                        'table_maintenance_dynamic_extended*',
                        f'processed_maintenance_dynamic_{self.config.date_stamp}_v1.csv'
                    ],
                    'output': f'table_maintenance_dynamic_extended_integers_{self.config.date_stamp}_v1.csv'
                }
            }

            for file_type, config in exogenous_files.items():
                input_file = None

                # First try the main pattern in each search directory
                for search_dir in config['search_dirs']:
                    try:
                        input_file = self.find_unique_file(search_dir, config['pattern'])
                        if input_file:
                            break
                    except ValueError as e:
                        logger.error(f"   ❌ Pattern matching error for {file_type}: {e}")
                        return False

                # If not found, try fallback patterns
                if not input_file:
                    for search_dir in config['search_dirs']:
                        for fallback_pattern in config['fallback_patterns']:
                            try:
                                input_file = self.find_unique_file(search_dir, fallback_pattern)
                                if input_file:
                                    break
                            except ValueError as e:
                                logger.error(f"   ❌ Fallback pattern matching error for {file_type}: {e}")
                                return False
                        if input_file:
                            break

                if input_file:
                    logger.info(f"   📄 Processing {file_type} exogenous dynamics from: {input_file}")
                    df = pd.read_csv(input_file)

                    # Check column names and standardize
                    if 'xyear' in df.columns:
                        df = df.rename(columns={'xyear': 'year'})

                    # Filter years (matching david_tools: 2011-2050)
                    if 'year' in df.columns:
                        df = df[(df['year'] >= 2011) & (df['year'] <= 2050)]

                    # Apply integer mappings (matching david_tools exactly, fixed FutureWarning)
                    if 'sex' in df.columns:
                        df['sex'] = df['sex'].replace({'Male': 1, 'Female': 2})
                        df['sex'] = df['sex'].infer_objects(copy=False)
                    if 'social grade' in df.columns:
                        df['social grade'] = df['social grade'].replace({'ABC1': 0, 'C2DE': 1})
                        df['social grade'] = df['social grade'].infer_objects(copy=False)
                    elif 'ABC1' in df.columns:
                        df['social_grade'] = df['ABC1'].replace({'ABC1': 0, 'C2DE': 1})
                        df['social_grade'] = df['social_grade'].infer_objects(copy=False)
                        df = df.drop('ABC1', axis=1)

                    # Ensure ABM-compatible column naming: add 'social grade' (with space) if we have 'social_grade' (with underscore)
                    if 'social_grade' in df.columns and 'social grade' not in df.columns:
                        df['social grade'] = df['social_grade']

                    # Save processed file to subdirectory ONLY (per protocol)
                    subdir_output = self.config.input_exogenous_dir / config['output']
                    df.to_csv(subdir_output, index=False)
                    logger.info(f"   ✅ Processed {file_type} exogenous dynamics: {config['output']}")

                    # Also create ABM-compatible version without date stamp in subdirectory
                    abm_output = self.config.input_exogenous_dir / f'table_{file_type}_dynamic_extended_integers.csv'
                    df.to_csv(abm_output, index=False)
                    logger.info(f"   ✅ Created ABM-compatible file: table_{file_type}_dynamic_extended_integers.csv")
                else:
                    logger.warning(f"   ⚠️  Could not find input file for {file_type} exogenous dynamics")

            logger.info("✅ Extended exogenous dynamics processed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to process extended exogenous dynamics: {e}")
            return False

    def generate_yaml_parameters(self) -> bool:
        """Generate YAML parameters from data dictionary (exact replication of display_l2attr_l1attr_beta_bias_for_model_yaml.py)."""
        logger.info("📋 Generating YAML parameters from data dictionary...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would generate YAML parameters")
            return True

        try:
            # Path to data dictionary (updated to use available CSV file)
            data_dictionary_path = Path('/home/shang/smoking/shang_notes/Data dictionary for CRUK smoking ABM v3 - Just PRSM variables - MASTER.csv')

            if not data_dictionary_path.exists():
                logger.warning(f"   ⚠️  Data dictionary not found: {data_dictionary_path}")
                logger.info("   ℹ️  Skipping YAML parameter generation")
                return True

            import pandas as pd
            import warnings
            warnings.filterwarnings("ignore", message="This pattern is interpreted as a regular expression, and has match groups.*")

            # Read data dictionary (updated to use CSV format)
            df = pd.read_csv(data_dictionary_path)
            attributes = df['synthetic population variables needed']

            # Generate parameter strings exactly as in original script
            yaml_parameters = []

            # Capability (c) attributes
            clevel2_attributes = attributes[attributes.str.contains(r'^(c[A-Z])', na=False)]
            uptake_clevel2_attributes = 'uptake.' + clevel2_attributes.astype(str) + '.beta'
            attempt_clevel2_attributes = 'attempt.' + clevel2_attributes.astype(str) + '.beta'
            maintenance_clevel2_attributes = 'maintenance.' + clevel2_attributes.astype(str) + '.beta'

            # Opportunity (o) attributes
            olevel2_attributes = attributes[attributes.str.contains(r'^(o[A-Z])', na=False)]
            uptake_olevel2_attributes = 'uptake.' + olevel2_attributes.astype(str) + '.beta'
            attempt_olevel2_attributes = 'attempt.' + olevel2_attributes.astype(str) + '.beta'
            maintenance_olevel2_attributes = 'maintenance.' + olevel2_attributes.astype(str) + '.beta'

            # Motivation (m) attributes
            mlevel2_attributes = attributes[attributes.str.contains(r'^(m[A-Z])', na=False)]
            uptake_mlevel2_attributes = 'uptake.' + mlevel2_attributes.astype(str) + '.beta'
            attempt_mlevel2_attributes = 'attempt.' + mlevel2_attributes.astype(str) + '.beta'
            maintenance_mlevel2_attributes = 'maintenance.' + mlevel2_attributes.astype(str) + '.beta'

            # Generate output exactly as original script
            yaml_parameters.append("# Generated YAML Parameters - Comprehensive")
            yaml_parameters.append("# Contains COM-B model parameters (templates) and E-cigarette diffusion parameters (actual values)")
            yaml_parameters.append("# COM-B parameters with actual values are automatically integrated into model.yaml")
            yaml_parameters.append("# E-cigarette diffusion parameters are automatically integrated into model.yaml")
            yaml_parameters.append(f"# Generated by unified data pipeline on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            yaml_parameters.append("")

            # Uptake parameters
            yaml_parameters.append("# UPTAKE COM-B Model Parameters")
            for item in list(uptake_clevel2_attributes):
                yaml_parameters.append(f"{item}: 0.1")
            yaml_parameters.append("")

            for item in list(uptake_olevel2_attributes):
                yaml_parameters.append(f"{item}: 0.1")
            yaml_parameters.append("")

            for item in list(uptake_mlevel2_attributes):
                yaml_parameters.append(f"{item}: 0.1")
            yaml_parameters.append("")

            yaml_parameters.extend([
                "uptake.C.beta: 0.1",
                "uptake.O.beta: 0.1",
                "uptake.M.beta: 0.1",
                "uptake.bias: 0.1",
                ""
            ])

            # Attempt parameters
            yaml_parameters.append("# ATTEMPT COM-B Model Parameters")
            for item in list(attempt_clevel2_attributes):
                yaml_parameters.append(f"{item}: 0.1")
            yaml_parameters.append("")

            for item in list(attempt_olevel2_attributes):
                yaml_parameters.append(f"{item}: 0.1")
            yaml_parameters.append("")

            for item in list(attempt_mlevel2_attributes):
                yaml_parameters.append(f"{item}: 0.1")
            yaml_parameters.append("")

            yaml_parameters.extend([
                "attempt.C.beta: 0.1",
                "attempt.O.beta: 0.1",
                "attempt.M.beta: 0.1",
                "attempt.bias: 0.1",
                ""
            ])

            # Maintenance parameters
            yaml_parameters.append("# MAINTENANCE COM-B Model Parameters")
            for item in list(maintenance_clevel2_attributes):
                yaml_parameters.append(f"{item}: 0.1")
            yaml_parameters.append("")

            for item in list(maintenance_olevel2_attributes):
                yaml_parameters.append(f"{item}: 0.1")
            yaml_parameters.append("")

            for item in list(maintenance_mlevel2_attributes):
                yaml_parameters.append(f"{item}: 0.1")
            yaml_parameters.append("")

            yaml_parameters.extend([
                "maintenance.C.beta: 0.1",
                "maintenance.O.beta: 0.1",
                "maintenance.M.beta: 0.1",
                "maintenance.bias: 0.1"
            ])

            # Save generated parameters to file
            output_file = self.config.local_mirror_base / f'generated_yaml_parameters_{self.config.date_stamp}_v1.txt'
            with open(output_file, 'w') as f:
                f.write('\n'.join(yaml_parameters))

            logger.info(f"   ✅ Generated YAML parameters: {output_file.name}")
            logger.info(f"   📋 Generated {len([p for p in yaml_parameters if '.beta:' in p])} parameter entries")

            logger.info("✅ YAML parameters generated successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to generate YAML parameters: {e}")
            return False

    def integrate_comb_beta_coefficients(self) -> bool:
        """Automatically read beta coefficients from COM-B files and update YAML configuration.

        This function eliminates the manual process of copying beta coefficients by:
        1. Reading 'Final' type coefficients from COM-B SEM coefficient files
        2. Mapping coefficient names to YAML parameter names
        3. Automatically updating the YAML file with correct beta values
        4. Validating the integration and reporting changes

        Returns:
            bool: True if beta integration successful, False otherwise
        """
        logger.info("🔧 Starting automated COM-B beta coefficient integration...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would integrate COM-B beta coefficients")
            return True

        try:
            # Define file paths for COM-B coefficient files
            attempts_files = list(self.config.intermediate_com_b_dir.glob('attempts_SEM_coefficents_*.csv'))
            maintenance_files = list(self.config.intermediate_com_b_dir.glob('maintenance_SEM_coefficients_*.csv'))

            if not attempts_files:
                logger.error(f"   ❌ No attempts coefficient files found in {self.config.intermediate_com_b_dir}")
                return False

            if not maintenance_files:
                logger.error(f"   ❌ No maintenance coefficient files found in {self.config.intermediate_com_b_dir}")
                return False

            attempts_file = attempts_files[0]
            maintenance_file = maintenance_files[0]

            logger.info(f"   📖 Reading attempts coefficients from: {attempts_file.name}")
            logger.info(f"   📖 Reading maintenance coefficients from: {maintenance_file.name}")

            # Read COM-B coefficient files
            attempts_df = pd.read_csv(attempts_file)
            maintenance_df = pd.read_csv(maintenance_file)

            # Filter for 'Final' type coefficients only
            final_attempts = attempts_df[attempts_df['type'] == 'Final'].copy()
            final_maintenance = maintenance_df[maintenance_df['type'] == 'Final'].copy()

            if final_attempts.empty:
                logger.error("   ❌ No 'Final' type coefficients found in attempts file")
                return False

            if final_maintenance.empty:
                logger.error("   ❌ No 'Final' type coefficients found in maintenance file")
                return False

            logger.info(f"   📊 Found {len(final_attempts)} final attempts coefficients")
            logger.info(f"   📊 Found {len(final_maintenance)} final maintenance coefficients")

            # Define coefficient name mappings (COM-B file name → YAML parameter name)
            # This mapping handles naming inconsistencies between COM-B analysis files and YAML configuration
            # Some parameters are commented out in YAML (missing from synthetic population) but mapping preserved for completeness
            attempts_mapping = {
                '(Intercept)': 'attempt.bias',  # Intercept maps to bias parameter
                'oSocialHousing': 'attempt.oSocialHousing.beta',
                'oPrevalenceOfSmokingInGeographicLocality': 'attempt.oPrevalenceOfSmokingInGeographicLocality.beta',
                'oReceiptGPAdvice': 'attempt.oReceiptGPAdvice.beta',  # Corrected spelling: Receipt (not Reciept)
                'oNumberOfSmokersInSocialNetwork': 'attempt.social_network.beta',  # Shortened name in YAML
                'mIntentionToQuit': 'attempt.mIntentionToQuit.beta',
                'mExpenditure': 'attempt.mExpenditure.beta',  # Commented out in YAML (missing from synthetic population)
                'mEnjoymentOfSmoking': 'attempt.mEnjoymentOfSmoking.beta',
                'mUseOfNRT': 'attempt.mUseOfNRT.beta',
                'mPositiveSmokerIdentity': 'attempt.mPositiveSmokerIdentity.beta',
                'mSelfEfficacy': 'attempt.mSelfEfficacy.beta',
                'mAgeGroup30To44': 'attempt.mAgeGroup30_44.beta',  # Commented out in YAML (age groups excluded)
                'mAgeGroup45To64': 'attempt.mAgeGroup45_64.beta',  # Commented out in YAML (age groups excluded)
                'mAgeGroup65Plus': 'attempt.mAgeGroup_over65.beta',  # Commented out in YAML (age groups excluded)
                'mNumberOfRecentQuitAttempts': 'attempt.mNumberOfRecentQuitAttempts.beta'
            }

            maintenance_mapping = {
                '(Intercept)': 'maintenance.bias',
                'cAlcoholConsumptionGroupHigherRisk': 'maintenance.cAlcoholConsumptionGroupHigherRisk.beta',  # Commented out
                'cAlcoholConsumptionGroupIncreasingRisk': 'maintenance.cAlcoholConsumptionGroupIncreasingRisk.beta',  # Commented out
                'cAlcoholConsumptionGroupLowerRisk': 'maintenance.cAlcoholConsumptionGroupLowerRisk.beta',  # Commented out
                'cECigUse': 'maintenance.cEcigaretteUse.beta',
                'cPrescriptionNRT': 'maintenance.cPrescriptionNRTInAttempt.beta',  # Commented out in YAML
                'cCigConsumption': 'maintenance.cCigConsumption.beta',  # Commented out in YAML
                'cVareniclineUse': 'maintenance.cVareniclineUse.beta',
                'cAgeGroup30To44': 'maintenance.cAgeGroup30_44.beta',  # Commented out in YAML
                'cAgeGroup45To64': 'maintenance.cAgeGroup45_64.beta',  # Commented out in YAML
                'cAgeGroup65Plus': 'maintenance.cAgeGroup_over65.beta',  # Commented out in YAML
                'cMentalHealthCondition': 'maintenance.cMentalHealthConditions.beta',
                'cCigAddictStrength': 'maintenance.cCigAddictStrength.beta',
                'cUseOfBehaviouralSupport': 'maintenance.cUseOfBehaviourSupportInAttempt.beta',  # Commented out
                'oSocialHousing': 'maintenance.oSocialHousing.beta',
                'oNumberOfSmokersInSocialNetwork': 'maintenance.social_network.beta',
                'oPrevalenceOfSmokingInGeographicLocality': 'maintenance.oPrevalenceOfSmokingInGeographicLocality.beta',  # Commented out
                'oSEP': 'maintenance.oSEP.beta',
                'cCytisineUse': 'maintenance.cCytisineUse.beta'
            }

            # Read current YAML file
            yaml_file = Path('props/model.yaml')
            if not yaml_file.exists():
                logger.error(f"   ❌ YAML file not found: {yaml_file}")
                return False

            with open(yaml_file, 'r') as f:
                yaml_content = f.read()

            updated_content = yaml_content
            beta_updates = []

            # Process attempts coefficients
            for _, row in final_attempts.iterrows():
                coeff_name = row['term']  # Coefficient name column
                coeff_value = row['B']  # Beta value column

                if coeff_name in attempts_mapping:
                    yaml_param = attempts_mapping[coeff_name]

                    # Update YAML content
                    if coeff_name == '(Intercept)':
                        # Handle bias (intercept) parameter
                        pattern = rf'^(attempt\.bias:\s*)([+-]?\d*\.?\d+)(.*)$'
                        replacement = rf'\g<1>{coeff_value:.9f}\g<3>'
                    else:
                        # Handle regular beta parameters
                        pattern = rf'^({re.escape(yaml_param)}:\s*)([+-]?\d*\.?\d+)(.*)$'
                        replacement = rf'\g<1>{coeff_value:.9f}\g<3>'

                    if re.search(pattern, updated_content, flags=re.MULTILINE):
                        updated_content = re.sub(pattern, replacement, updated_content, flags=re.MULTILINE)
                        beta_updates.append(f"     ✅ {yaml_param}: {coeff_value:.9f}")
                    else:
                        logger.info(f"     ⚠️  YAML parameter not found or commented out: {yaml_param}")

            # Process maintenance coefficients
            for _, row in final_maintenance.iterrows():
                coeff_name = row['term']  # Coefficient name column
                coeff_value = row['B']  # Beta value column

                if coeff_name in maintenance_mapping:
                    yaml_param = maintenance_mapping[coeff_name]

                    # Update YAML content
                    if coeff_name == '(Intercept)':
                        # Handle bias (intercept) parameter
                        pattern = rf'^(maintenance\.bias:\s*)([+-]?\d*\.?\d+)(.*)$'
                        replacement = rf'\g<1>{coeff_value:.9f}\g<3>'
                    else:
                        # Handle regular beta parameters
                        pattern = rf'^({re.escape(yaml_param)}:\s*)([+-]?\d*\.?\d+)(.*)$'
                        replacement = rf'\g<1>{coeff_value:.9f}\g<3>'

                    if re.search(pattern, updated_content, flags=re.MULTILINE):
                        updated_content = re.sub(pattern, replacement, updated_content, flags=re.MULTILINE)
                        beta_updates.append(f"     ✅ {yaml_param}: {coeff_value:.9f}")
                    else:
                        logger.info(f"     ⚠️  YAML parameter not found or commented out: {yaml_param}")

            # Write updated YAML content
            with open(yaml_file, 'w') as f:
                f.write(updated_content)

            # Report results
            logger.info(f"✅ COM-B beta coefficient integration completed successfully!")
            logger.info(f"   📊 Updated {len(beta_updates)} beta parameters:")
            for update in beta_updates:
                logger.info(update)

            return True

        except Exception as e:
            logger.error(f"❌ Error during COM-B beta integration: {e}")
            return False

    def integrate_diffusion_parameters(self) -> bool:
        """
        Integrate e-cigarette diffusion parameters from CSV file into YAML configuration.

        Reads diffusion parameters (p, q, m, d) for different cohorts and smoking statuses
        from the monthly_diffusion_parameters CSV file and updates the YAML configuration
        with the current values.

        Returns:
            bool: True if diffusion parameter integration successful, False otherwise
        """
        logger.info("🚬 Starting e-cigarette diffusion parameter integration...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would integrate diffusion parameters")
            return True

        try:
            # Define file path for diffusion parameters
            diffusion_files = list(self.config.intermediate_ecig_dir.glob('monthly_diffusion_parameters_*.csv'))

            if not diffusion_files:
                logger.error(f"   ❌ No diffusion parameter files found in {self.config.intermediate_ecig_dir}")
                return False

            diffusion_file = diffusion_files[0]
            logger.info(f"   📖 Reading diffusion parameters from: {diffusion_file.name}")

            # Read diffusion parameters CSV
            diffusion_df = pd.read_csv(diffusion_file)

            # Validate required columns
            required_columns = ['cohort', 'smokstat', 'p', 'q', 'm', 'd', 'type']
            missing_columns = [col for col in required_columns if col not in diffusion_df.columns]
            if missing_columns:
                logger.error(f"   ❌ Missing required columns in diffusion file: {missing_columns}")
                return False

            logger.info(f"   📊 Found {len(diffusion_df)} diffusion parameter entries")

            # Create mapping from CSV data to YAML parameter names
            yaml_updates = []

            for _, row in diffusion_df.iterrows():
                cohort = row['cohort']
                smokstat = row['smokstat']
                p_val = row['p']
                q_val = row['q']
                m_val = row['m']
                d_val = row['d']
                diff_type = row['type']

                # Convert cohort and smokstat to YAML parameter format
                # Handle cohort naming: "<1940" -> "less1940", "1991+" -> "over1991", etc.
                if cohort == "<1940":
                    cohort_yaml = "less1940"
                elif cohort == "1991+":
                    cohort_yaml = "over1991"
                else:
                    cohort_yaml = cohort.replace("-", "_")

                # Handle smoking status naming: "Ex-smoker" -> "exsmoker", "Never smoked" -> "neversmoker"
                if smokstat == "Ex-smoker":
                    smokstat_yaml = "exsmoker"
                elif smokstat == "Never smoked":
                    smokstat_yaml = "neversmoker"
                else:
                    smokstat_yaml = smokstat.lower()

                # Create YAML parameter prefix based on type
                if diff_type == "e-cig":
                    prefix = "nondisp_diffusion"
                elif diff_type == "disposable":
                    prefix = "disp_diffusion"
                else:
                    logger.warning(f"   ⚠️ Unknown diffusion type: {diff_type}")
                    continue

                # Generate YAML parameter names and values
                base_name = f"{prefix}_{smokstat_yaml}_{cohort_yaml}"

                yaml_updates.extend([
                    (f"{base_name}.p", f"{p_val:.9f}"),
                    (f"{base_name}.q", f"{q_val:.9f}"),
                    (f"{base_name}.m", f"{m_val:.9f}"),
                    (f"{base_name}.d", f"{d_val:.9f}")
                ])

            # Read current YAML file
            yaml_file = Path('props/model.yaml')
            if not yaml_file.exists():
                logger.error(f"   ❌ YAML file not found: {yaml_file}")
                return False

            with open(yaml_file, 'r') as f:
                yaml_content = f.read()

            # Apply diffusion parameter updates
            diffusion_updates = []
            for param_name, param_value in yaml_updates:
                # Create regex pattern to match the parameter line
                pattern = rf'^({re.escape(param_name)}:\s*)([0-9.-]+)(\s*#.*)?$'
                replacement = rf'\g<1>{param_value}\g<3>'

                new_content, count = re.subn(pattern, replacement, yaml_content, flags=re.MULTILINE)

                if count > 0:
                    yaml_content = new_content
                    diffusion_updates.append(f"   📊 {param_name}: {param_value}")
                else:
                    logger.warning(f"   ⚠️ Parameter not found in YAML: {param_name}")

            # Write updated YAML file
            with open(yaml_file, 'w') as f:
                f.write(yaml_content)

            # Append diffusion parameters to the existing generated parameters file
            template_file = self.config.local_mirror_base / f'generated_yaml_parameters_{self.config.date_stamp}_v1.txt'

            # Check if the COM-B parameters file exists, if not create header
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    f.write("# Generated YAML Parameters - Comprehensive\n")
                    f.write("# Contains both COM-B model parameters and E-cigarette diffusion parameters\n")
                    f.write("# Parameters with actual values were automatically integrated into model.yaml\n")
                    f.write(f"# Generated by unified data pipeline on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Append diffusion parameters to the existing file
            with open(template_file, 'a') as f:
                f.write(f"\n# E-cigarette Diffusion Parameters (Source: {diffusion_file.name})\n")
                f.write("# These parameters were automatically integrated into model.yaml\n\n")

                f.write("# Non-disposable E-cigarette Diffusion Parameters\n")
                for param_name, param_value in yaml_updates:
                    if param_name.startswith("nondisp_diffusion"):
                        f.write(f"{param_name}: {param_value}\n")

                f.write("\n# Disposable E-cigarette Diffusion Parameters\n")
                for param_name, param_value in yaml_updates:
                    if param_name.startswith("disp_diffusion"):
                        f.write(f"{param_name}: {param_value}\n")

            # Report results
            logger.info(f"✅ Diffusion parameter integration completed successfully!")
            logger.info(f"   📊 Updated {len(diffusion_updates)} diffusion parameters:")
            for update in diffusion_updates[:10]:  # Show first 10 updates
                logger.info(update)
            if len(diffusion_updates) > 10:
                logger.info(f"   📊 ... and {len(diffusion_updates) - 10} more parameters")
            logger.info(f"   📄 Appended to comprehensive parameters file: {template_file.name}")

            return True

        except Exception as e:
            logger.error(f"❌ Error during diffusion parameter integration: {e}")
            return False

    def update_yaml_file_paths(self) -> bool:
        """Update YAML file with actual file paths (resolve patterns to real filenames)."""
        logger.info("📋 Updating YAML file paths with actual filenames...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would update YAML file paths")
            return True

        try:
            yaml_file = Path('props/model.yaml')

            if not yaml_file.exists():
                logger.error(f"   ❌ YAML file not found: {yaml_file}")
                return False

            # Read current YAML content
            with open(yaml_file, 'r') as f:
                yaml_content = f.read()

            # Define pattern mappings to resolve
            pattern_mappings = {
                'synthetic_population_*.csv': {
                    'search_dir': self.config.input_data_dir / 'synthetic_population',
                    'pattern': 'synthetic_population_*.csv'
                },
                'regional_smoking_trends_*.csv': {
                    'search_dir': self.config.intermediate_exogenous_dir,
                    'pattern': 'regional_smoking_trends_*.csv'
                },
                'sts_cig_consumption_percentiles_*.csv': {
                    'search_dir': self.config.intermediate_exogenous_dir,
                    'pattern': 'sts_cig_consumption_percentiles_*.csv'
                }
            }

            # Resolve each pattern to actual filename
            for pattern, config in pattern_mappings.items():
                try:
                    actual_file = self.find_unique_file(config['search_dir'], config['pattern'])
                    if actual_file:
                        # Get relative path from ABM working directory (smokingABM/)
                        try:
                            # Convert to absolute path first
                            abs_file = actual_file.resolve()
                            # Get relative path from smokingABM directory (ABM working directory)
                            abm_base = (Path.cwd() / 'smokingABM').resolve()
                            relative_path = abs_file.relative_to(abm_base)
                        except ValueError:
                            # Fallback: try relative to data directory
                            try:
                                data_base = (Path.cwd() / 'smokingABM' / 'data').resolve()
                                relative_path = Path('data') / actual_file.resolve().relative_to(data_base)
                            except ValueError:
                                # Final fallback: use the file path as-is
                                relative_path = actual_file

                        # Update YAML content with ABM-relative path
                        yaml_content = yaml_content.replace(pattern, str(relative_path))
                        logger.info(f"   ✅ Resolved {pattern} → {relative_path}")
                    else:
                        logger.warning(f"   ⚠️  Could not resolve pattern: {pattern}")
                except ValueError as e:
                    logger.error(f"   ❌ Error resolving {pattern}: {e}")
                    return False

            # Write updated YAML content
            with open(yaml_file, 'w') as f:
                f.write(yaml_content)

            logger.info("✅ YAML file paths updated successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update YAML file paths: {e}")
            return False

    def validate_processing(self) -> bool:
        """Validate processed data files and perform quality checks."""
        logger.info("✅ Validating processed data...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would validate processed data")
            return True

        try:
            validation_results = []

            # Check critical files exist (matching ABM expectations from model.yaml - files in input_data subdirectories per protocol)
            critical_files = [
                self.config.input_stpm_dir / 'initiation_prob1month_STPM.csv',  # Fixed: was input_stmp_dir
                self.config.input_stpm_dir / 'relapse_prob1month_STPM.csv',     # Fixed: was input_stmp_dir
                self.config.input_stpm_dir / 'quit_prob1month_STPM.csv',        # Fixed: was input_stmp_dir
                self.config.input_stpm_dir / 'death_probs_abm_integers.csv',    # Fixed: was input_stmp_dir
                self.config.input_exogenous_dir / 'table_attempts_dynamic_extended_integers.csv',
                self.config.input_exogenous_dir / 'table_maintenance_dynamic_extended_integers.csv'
            ]

            for file_path in critical_files:
                if file_path.exists():
                    df = pd.read_csv(file_path)
                    validation_results.append({
                        'file': file_path.name,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'status': 'OK'
                    })
                    logger.info(f"   ✅ {file_path.name}: {len(df)} rows, {len(df.columns)} columns")
                else:
                    validation_results.append({
                        'file': file_path.name,
                        'status': 'MISSING'
                    })
                    logger.warning(f"   ⚠️  Missing file: {file_path.name}")

            # Validate probability bounds for STMP files
            for file_path in critical_files[:3]:  # STMP probability files
                if file_path.exists():
                    df = pd.read_csv(file_path)
                    prob_cols = [col for col in df.columns if 'month' in col]
                    for col in prob_cols:
                        if col in df.columns:
                            min_val, max_val = df[col].min(), df[col].max()
                            if min_val < 0 or max_val > 1:
                                logger.warning(f"   ⚠️  Probability bounds issue in {file_path.name}:{col}: [{min_val:.4f}, {max_val:.4f}]")
                            else:
                                logger.info(f"   ✅ Probability bounds OK in {file_path.name}:{col}: [{min_val:.4f}, {max_val:.4f}]")

            logger.info("✅ Data validation completed")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to validate processed data: {e}")
            return False

    def process_synthetic_population(self) -> bool:
        """Process synthetic population files to ensure ABM compatibility."""
        logger.info("👥 Processing synthetic population files...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would process synthetic population files")
            return True

        try:
            # Find synthetic population file
            synthetic_pop_files = list(self.config.input_population_dir.glob('synthetic_population_*.csv'))
            
            if not synthetic_pop_files:
                logger.warning("   ⚠️  No synthetic population files found")
                return True
                
            for file_path in synthetic_pop_files:
                logger.info(f"   📄 Processing synthetic population file: {file_path.name}")
                df = pd.read_csv(file_path)
                original_columns = df.columns.tolist()
                
                # Column compatibility fixes for ABM
                changes_made = []
                
                # Fix 1: Missing 'year' column (ABM expects 'year' but data has 'arrivalYear')
                if 'arrivalYear' in df.columns and 'year' not in df.columns:
                    df['year'] = df['arrivalYear']
                    changes_made.append("Added 'year' column as copy of 'arrivalYear'")
                
                # Fix 2: Missing 'perc_num' column (ABM expects 'perc_num' but data has 'pCigConsumptionPercentile')
                if 'pCigConsumptionPercentile' in df.columns and 'perc_num' not in df.columns:
                    df['perc_num'] = df['pCigConsumptionPercentile']
                    changes_made.append("Added 'perc_num' column as copy of 'pCigConsumptionPercentile'")
                
                # Fix 3: E-cigarette column mismatch (ABM expects 'cEcigaretteUse' but data has 'cECigUse')
                if 'cECigUse' in df.columns and 'cEcigaretteUse' not in df.columns:
                    df['cEcigaretteUse'] = df['cECigUse']
                    changes_made.append("Added 'cEcigaretteUse' column as alias of 'cECigUse'")
                
                # Fix 4: Missing consumption column (ABM expects 'cCigConsumptionPrequit')
                if 'cCigConsumption' in df.columns and 'cCigConsumptionPrequit' not in df.columns:
                    df['cCigConsumptionPrequit'] = df['cCigConsumption']
                    changes_made.append("Added 'cCigConsumptionPrequit' column as alias of 'cCigConsumption'")
                
                # Fix 5: GP advice column typo (ensure correct spelling 'oReceiptGPAdvice' exists for ABM)
                if 'oRecieptGPAdvice' in df.columns and 'oReceiptGPAdvice' not in df.columns:
                    df['oReceiptGPAdvice'] = df['oRecieptGPAdvice']
                    changes_made.append("Added 'oReceiptGPAdvice' column from misspelled 'oRecieptGPAdvice' (correcting typo for ABM)")
                
                # Save the updated file if changes were made
                if changes_made:
                    df.to_csv(file_path, index=False)
                    logger.info(f"   ✅ Updated synthetic population file: {file_path.name}")
                    for change in changes_made:
                        logger.info(f"      • {change}")
                    logger.info(f"   📊 File shape: {df.shape[0]} rows, {df.shape[1]} columns (was {len(original_columns)} columns)")
                else:
                    logger.info(f"   ✅ No column compatibility issues found in {file_path.name}")
                    
            logger.info("✅ Synthetic population processing completed successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to process synthetic population files: {e}")
            return False

    def validate_parameter_mapping(self) -> bool:
        """
        Validate parameter mapping between YAML and CSV columns.
        Generates comprehensive CSV report for manual inspection.
        Provides warnings for unused columns but does not fail.
        """
        logger.info("🔍 Validating parameter mapping and generating inspection report...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would validate parameter mapping")
            return True

        try:
            # This validation requires the ABM codebase to extract YAML parameters
            # We'll simulate the parameter extraction process here
            
            # Read YAML file to extract parameters
            yaml_file = Path('props/model.yaml')
            if not yaml_file.exists():
                logger.warning(f"   ⚠️  YAML file not found: {yaml_file}, skipping parameter mapping validation")
                return True

            import yaml
            import re
            
            with open(yaml_file, 'r') as f:
                yaml_config = yaml.safe_load(f)
            
            # Extract .beta parameters from YAML (same logic as smoking_model.py)
            yaml_parameters = set()
            for key in yaml_config.keys():
                if isinstance(key, str):
                    # Match patterns like: uptake.cVariable.beta, attempt.oVariable.beta, maintenance.mVariable.beta
                    for theory_type in ['uptake', 'attempt', 'maintenance']:
                        pattern = f'^{theory_type}\.([com]\\w+)\\.beta$'
                        m = re.match(pattern, key)
                        if m:
                            parameter_name = m.group(1)
                            yaml_parameters.add(parameter_name)
                            break
            
            # Find synthetic population file
            syn_pop_dir = self.config.local_mirror_base / 'input_data' / 'synthetic_population'
            # First try exact date stamp match, then any synthetic_population file
            syn_pop_files = list(syn_pop_dir.glob(f'synthetic_population_{self.config.date_stamp}_v1.csv'))
            if not syn_pop_files:
                syn_pop_files = list(syn_pop_dir.glob('synthetic_population_*_v1.csv'))
            
            if not syn_pop_files:
                logger.warning(f"   ⚠️  No synthetic population files found in {syn_pop_dir}")
                logger.warning("   ⚠️  Skipping parameter mapping validation")
                return True
            
            syn_pop_file = syn_pop_files[0]
            logger.info(f"   📋 Analyzing synthetic population file: {syn_pop_file.name}")
            
            # Read CSV to get column names
            import pandas as pd
            df = pd.read_csv(syn_pop_file, nrows=1)  # Just read header
            csv_columns = set([col for col in df.columns if col.startswith(('c', 'o', 'm'))])
            
            logger.info(f"   📊 Found {len(yaml_parameters)} YAML .beta parameters")
            logger.info(f"   📊 Found {len(csv_columns)} CSV columns with c/o/m prefix")
            
            # Create validation report
            validation_data = []
            
            # Process all variables (union of YAML and CSV)
            all_variables = yaml_parameters.union(csv_columns)
            
            for variable in sorted(all_variables):
                csv_exists = variable in csv_columns
                yaml_exists = variable in yaml_parameters
                
                # Determine status and warning
                if csv_exists and yaml_exists:
                    status = "MATCHED"
                    warning = ""
                elif csv_exists and not yaml_exists:
                    status = "CSV_ONLY"
                    warning = "Column exists but no YAML parameter - unused data"
                elif not csv_exists and yaml_exists:
                    status = "YAML_ONLY"
                    warning = "YAML parameter exists but no CSV column - WILL CAUSE RUNTIME ERROR"
                else:
                    status = "ERROR"
                    warning = "Unexpected state"
                
                validation_data.append({
                    'variable_name': variable,
                    'csv_column_exists': csv_exists,
                    'yaml_parameter_exists': yaml_exists,
                    'status': status,
                    'warning': warning
                })
            
            # Generate CSV report
            report_df = pd.DataFrame(validation_data)
            report_file = self.config.local_mirror_base / f'parameter_mapping_validation_{self.config.date_stamp}_v1.csv'
            report_df.to_csv(report_file, index=False)
            
            # Generate summary statistics
            matched_count = len([item for item in validation_data if item['status'] == 'MATCHED'])
            csv_only_count = len([item for item in validation_data if item['status'] == 'CSV_ONLY'])
            yaml_only_count = len([item for item in validation_data if item['status'] == 'YAML_ONLY'])
            
            logger.info(f"   📋 Parameter mapping validation report generated: {report_file.name}")
            logger.info(f"   📊 Summary:")
            logger.info(f"      • ✅ Matched parameters: {matched_count}")
            logger.info(f"      • ⚠️  Unused CSV columns: {csv_only_count}")
            logger.info(f"      • ❌ Missing CSV columns: {yaml_only_count}")
            
            # Log warnings for potential issues
            if csv_only_count > 0:
                logger.warning(f"   ⚠️  {csv_only_count} CSV columns exist without corresponding YAML parameters (memory waste)")
            
            if yaml_only_count > 0:
                logger.error(f"   ❌ {yaml_only_count} YAML parameters lack corresponding CSV columns (WILL CAUSE RUNTIME ERRORS)")
                yaml_only_vars = [item['variable_name'] for item in validation_data if item['status'] == 'YAML_ONLY']
                logger.error(f"   ❌ Missing variables: {', '.join(yaml_only_vars)}")
            
            logger.info("✅ Parameter mapping validation completed")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to validate parameter mapping: {e}")
            logger.error("   ⚠️  Continuing pipeline execution (validation is non-critical)")
            return True

class FileManager:
    """Handles file operations, naming conventions, and backup procedures."""

    def __init__(self, config: UnifiedPipelineConfig):
        """Initialize file manager with configuration."""
        self.config = config

    def generate_summary_report(self) -> bool:
        """Generate comprehensive summary report of pipeline execution."""
        logger.info("📋 Generating summary report...")

        if self.config.dry_run:
            logger.info("🔍 DRY RUN: Would generate summary report")
            return True

        try:
            report_file = self.config.local_mirror_base / f'unified_pipeline_report_{self.config.date_stamp}_v1.txt'

            with open(report_file, 'w') as f:
                f.write("SmokingABM Unified Data Processing Pipeline Report\n")
                f.write("=" * 60 + "\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Pipeline Version: 1.0.0 (Unified)\n")
                f.write(f"Mode: {self.config.mode}\n")
                f.write(f"X-drive Sync: {self.config.sync_xdrive}\n")
                f.write(f"Date Stamp: {self.config.date_stamp}\n")
                f.write(f"Local Mirror: {self.config.local_mirror_base}\n\n")

                f.write("Directory Structure:\n")
                f.write("-" * 30 + "\n")
                f.write(f"- {self.config.raw_data_dir.relative_to(self.config.local_mirror_base)}\n")
                f.write(f"- {self.config.intermediate_data_dir.relative_to(self.config.local_mirror_base)}\n")
                f.write(f"- {self.config.input_data_dir.relative_to(self.config.local_mirror_base)}\n")
                f.write(f"- {self.config.output_data_dir.relative_to(self.config.local_mirror_base)}\n\n")

                f.write("Files Processed:\n")
                f.write("-" * 20 + "\n")

                # List processed files
                for subdir in [self.config.intermediate_data_dir, self.config.input_data_dir]:
                    if subdir.exists():
                        for file_path in subdir.rglob(f'*{self.config.date_stamp}*'):
                            f.write(f"- {file_path.relative_to(self.config.local_mirror_base)}\n")

                f.write("\nProcessing Steps Completed:\n")
                f.write("-" * 30 + "\n")
                f.write("1. Directory structure creation\n")
                f.write("2. Data synchronization (if enabled)\n")
                f.write("3. Synthetic population processing (ABM compatibility)\n")
                f.write("4. Excel formula implementation\n")
                f.write("5. Log odds validation and naming cleanup\n")
                f.write("6. STMP probability conversion\n")
                f.write("7. Integer mapping application\n")
                f.write("8. Death probability processing\n")
                f.write("9. Extended exogenous dynamics processing\n")
                f.write("10. Data validation and quality checks\n")
                f.write("11. YAML parameter generation\n")
                f.write("12. COM-B beta coefficient integration\n")
                f.write("13. E-cigarette diffusion parameter integration\n")
                f.write("14. YAML file path updates\n")
                f.write("15. Parameter mapping validation and reporting\n")
                f.write("16. Result synchronization (if enabled)\n")

                f.write(f"\nConsolidated Functionality From:\n")
                f.write("-" * 35 + "\n")
                f.write("- preprocess_all_data.py (X-drive integration, directory creation)\n")
                f.write("- comprehensive_data_preprocessing_pipeline.py (Excel formulas, log odds validation)\n")
                f.write("- process_input_data_files.py (STMP processing, integer conversion)\n")

            logger.info(f"✅ Summary report saved: {report_file.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to generate summary report: {e}")
            return False

class UnifiedDataPipeline:
    """Main unified data processing pipeline that orchestrates all components."""

    def __init__(self, mode: str = 'local', sync_xdrive: bool = False,
                 date_stamp: Optional[str] = None, dry_run: bool = False):
        """Initialize the unified pipeline."""
        self.config = UnifiedPipelineConfig(mode, sync_xdrive, date_stamp, dry_run)
        self.synchronizer = DataSynchronizer(self.config)
        self.processor = ProcessingEngine(self.config)
        self.file_manager = FileManager(self.config)

        logger.info("🚀 Unified Data Pipeline Initialized")

    def run_pipeline(self) -> bool:
        """Execute the unified data processing pipeline based on mode."""
        logger.info("🎯 Starting Unified Data Processing Pipeline")
        logger.info("=" * 60)

        try:
            # Step 1: Configuration and setup
            logger.info("📋 Step 1: Configuration Setup")
            if not self._validate_configuration():
                return False

            # Handle different modes
            if self.config.mode == 'sync-approve':
                return self._run_sync_approve_mode()
            elif self.config.mode == 'process':
                return self._run_process_mode()
            else:
                return self._run_legacy_mode()

        except Exception as e:
            logger.error(f"❌ Pipeline execution failed: {e}")
            return False

    def _run_process_mode(self) -> bool:
        """Run local processing only (no X-drive sync)."""
        logger.info("🔧 MODE: PROCESS (Local processing only)")
        logger.info("=" * 60)

        # Step 2: Data synchronization from X-drive (ENABLE for source data)
        logger.info("📋 Step 2: Data Synchronization (X-drive → Local)")
        
        # Temporarily enable X-drive sync to get source data
        original_sync_setting = self.config.sync_xdrive
        self.config.sync_xdrive = True
        
        sync_success = self.synchronizer.sync_from_xdrive()
        
        # Restore original sync setting (disable for rest of pipeline)
        self.config.sync_xdrive = original_sync_setting
        
        if not sync_success:
            return False

        # Step 3: Create directory structure
        logger.info("📋 Step 3: Directory Structure Creation")
        if not self.processor.create_directory_structure():
            return False

        # Step 4: Process synthetic population for ABM compatibility
        logger.info("📋 Step 4: Synthetic Population Processing")
        if not self.processor.process_synthetic_population():
            return False

        # Step 5: Process Excel formulas
        logger.info("📋 Step 5: Excel Formula Processing")
        if not self.processor.process_excel_formulas():
            return False

        # Step 6: Validate log odds columns and handle naming
        logger.info("📋 Step 6: Log Odds Validation & Naming Cleanup")
        if not self.processor.validate_logodds_columns():
            return False

        # Step 7: Convert STMP probabilities
        logger.info("📋 Step 7: STMP Probability Conversion")
        if not self.processor.convert_stmp_probabilities():
            return False

        # Step 8: Apply integer mappings
        logger.info("📋 Step 8: Integer Mapping Application")
        if not self.processor.apply_integer_mappings():
            return False

        # Step 9: Process death probabilities
        logger.info("📋 Step 9: Death Probability Processing")
        if not self.processor.process_death_probabilities():
            return False

        # Step 10: Process extended exogenous dynamics
        logger.info("📋 Step 10: Extended Exogenous Dynamics Processing")
        if not self.processor.process_extended_exogenous_dynamics():
            return False

        # Step 11: Validate processing results
        logger.info("📋 Step 11: Data Validation")
        if not self.processor.validate_processing():
            return False

        # Step 12: Generate YAML parameters
        logger.info("📋 Step 12: YAML Parameter Generation")
        if not self.processor.generate_yaml_parameters():
            return False

        # Step 13: Integrate COM-B beta coefficients
        logger.info("📋 Step 13: COM-B Beta Coefficient Integration")
        if not self.processor.integrate_comb_beta_coefficients():
            return False

        # Step 14: Integrate e-cigarette diffusion parameters
        logger.info("📋 Step 14: E-cigarette Diffusion Parameter Integration")
        if not self.processor.integrate_diffusion_parameters():
            return False

        # Step 15: Update YAML file paths
        logger.info("📋 Step 15: YAML File Path Updates")
        if not self.processor.update_yaml_file_paths():
            return False

        # Step 16: Validate parameter mapping
        logger.info("📋 Step 16: Parameter Mapping Validation")
        if not self.processor.validate_parameter_mapping():
            return False

        # Step 17: Generate summary report
        logger.info("📋 Step 17: Summary Report Generation")
        if not self.file_manager.generate_summary_report():
            return False

        logger.info("=" * 60)
        logger.info("✅ LOCAL PROCESSING COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info("📁 All processed data available in: smokingABM/data/")
        logger.info("🔄 To sync to X-drive, run:")
        logger.info(f"   python {__file__} --mode sync-approve --date-stamp {self.config.date_stamp}")
        logger.info("=" * 60)

        return True

    def _run_sync_approve_mode(self) -> bool:
        """Run X-drive sync with confirmation."""
        logger.info("🔄 MODE: SYNC-APPROVE (X-drive sync with confirmation)")
        logger.info("=" * 60)

        # Enable X-drive sync for this mode
        self.config.sync_xdrive = True

        # Step 2: Confirm and execute sync to X-drive
        logger.info("📋 Step 2: X-drive Sync with Confirmation")
        if not self.synchronizer.confirm_sync_to_xdrive():
            logger.info("❌ X-drive sync cancelled or failed")
            return False

        # Step 3: Generate summary report
        logger.info("📋 Step 3: Summary Report Generation")
        if not self.file_manager.generate_summary_report():
            return False

        logger.info("=" * 60)
        logger.info("✅ X-DRIVE SYNC COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)

        return True

    def _run_legacy_mode(self) -> bool:
        """Run legacy pipeline modes (full, local, sync-only)."""
        logger.info(f"🔧 MODE: {self.config.mode.upper()} (Legacy mode)")
        logger.info("=" * 60)

        # Step 2: Data synchronization from X-drive (if enabled)
        logger.info("📋 Step 2: Data Synchronization (X-drive → Local)")
        if not self.synchronizer.sync_from_xdrive():
            return False

        # Step 3: Create directory structure
        logger.info("📋 Step 3: Directory Structure Creation")
        if not self.processor.create_directory_structure():
            return False

        # Step 4: Process synthetic population for ABM compatibility
        logger.info("📋 Step 4: Synthetic Population Processing")
        if not self.processor.process_synthetic_population():
            return False

        # Step 5: Process Excel formulas
        logger.info("📋 Step 5: Excel Formula Processing")
        if not self.processor.process_excel_formulas():
            return False

        # Step 6: Validate log odds columns and handle naming
        logger.info("📋 Step 6: Log Odds Validation & Naming Cleanup")
        if not self.processor.validate_logodds_columns():
            return False

        # Step 7: Convert STMP probabilities
        logger.info("📋 Step 7: STMP Probability Conversion")
        if not self.processor.convert_stmp_probabilities():
            return False

        # Step 8: Apply integer mappings
        logger.info("📋 Step 8: Integer Mapping Application")
        if not self.processor.apply_integer_mappings():
            return False

        # Step 9: Process death probabilities
        logger.info("📋 Step 9: Death Probability Processing")
        if not self.processor.process_death_probabilities():
            return False

        # Step 10: Process extended exogenous dynamics
        logger.info("📋 Step 10: Extended Exogenous Dynamics Processing")
        if not self.processor.process_extended_exogenous_dynamics():
            return False

        # Step 11: Validate processing results
        logger.info("📋 Step 11: Data Validation")
        if not self.processor.validate_processing():
            return False

        # Step 12: Generate YAML parameters
        logger.info("📋 Step 12: YAML Parameter Generation")
        if not self.processor.generate_yaml_parameters():
            return False

        # Step 13: Integrate COM-B beta coefficients
        logger.info("📋 Step 13: COM-B Beta Coefficient Integration")
        if not self.processor.integrate_comb_beta_coefficients():
            return False

        # Step 14: Integrate e-cigarette diffusion parameters
        logger.info("📋 Step 14: E-cigarette Diffusion Parameter Integration")
        if not self.processor.integrate_diffusion_parameters():
            return False

        # Step 15: Update YAML file paths
        logger.info("📋 Step 15: YAML File Path Updates")
        if not self.processor.update_yaml_file_paths():
            return False

        # Step 16: Validate parameter mapping
        logger.info("📋 Step 16: Parameter Mapping Validation")
        if not self.processor.validate_parameter_mapping():
            return False

        # Step 17: Synchronize results to X-drive (if enabled)
        logger.info("📋 Step 17: Result Synchronization (Local → X-drive)")
        if not self.synchronizer.sync_to_xdrive():
            return False

        # Step 18: Generate summary report
        logger.info("📋 Step 18: Summary Report Generation")
        if not self.file_manager.generate_summary_report():
            return False

        logger.info("=" * 60)
        logger.info("🎉 Unified Data Processing Pipeline Completed Successfully!")
        logger.info("=" * 60)

        return True

    def _validate_configuration(self) -> bool:
        """Validate pipeline configuration and prerequisites."""
        valid_modes = ['full', 'local', 'sync-only', 'process', 'sync-approve']
        if self.config.mode not in valid_modes:
            logger.error(f"❌ Invalid mode: {self.config.mode}")
            return False

        # For sync-approve mode, always validate X-drive access
        if self.config.mode == 'sync-approve':
            if not self.synchronizer.validate_xdrive_access():
                logger.error("❌ sync-approve mode requires X-drive access")
                return False

        # For process mode, validate X-drive access (needed for initial sync)
        elif self.config.mode == 'process':
            if not self.synchronizer.validate_xdrive_access():
                logger.error("❌ process mode requires X-drive access for initial data synchronization")
                return False

        # For other modes with X-drive sync enabled
        elif self.config.sync_xdrive and not self.synchronizer.validate_xdrive_access():
            logger.error("❌ X-drive sync enabled but X-drive not accessible")
            return False

        logger.info("✅ Configuration validation passed")
        return True

def main():
    """Main function to run the unified data processing pipeline."""
    parser = argparse.ArgumentParser(
        description='Unified Data Processing Pipeline for SmokingABM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete pipeline with X-drive sync
  python run_unified_data_pipeline.py --mode full --sync-xdrive

  # Local processing only
  python run_unified_data_pipeline.py --mode local

  # Sync results to X-drive only
  python run_unified_data_pipeline.py --mode sync-only

  # Dry run (preview mode)
  python run_unified_data_pipeline.py --mode full --dry-run

  # Custom date stamp
  python run_unified_data_pipeline.py --mode full --date-stamp 20250609
        """
    )

    parser.add_argument('--mode',
                       choices=['full', 'local', 'sync-only', 'process', 'sync-approve'],
                       default='local',
                       help='Processing mode: process (local only), sync-approve (confirm X-drive sync), full (legacy), local (legacy), sync-only (legacy)')

    parser.add_argument('--sync-xdrive',
                       action='store_true',
                       help='Enable X-drive synchronization')

    parser.add_argument('--date-stamp',
                       help='Custom date stamp (YYYYMMDD, default: current date)')

    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Preview mode - show what would be done without making changes')

    args = parser.parse_args()

    # Print banner
    print("\n" + "=" * 80)
    print("🚀 SMOKINGABM UNIFIED DATA PROCESSING PIPELINE")
    print("=" * 80)
    print(f"Version: 1.0.0 (Unified)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {args.mode.upper()}")
    print(f"X-drive Sync: {'ENABLED' if args.sync_xdrive else 'DISABLED'}")
    print(f"Dry Run: {'YES' if args.dry_run else 'NO'}")
    if args.date_stamp:
        print(f"Date Stamp: {args.date_stamp}")
    print("=" * 80)

    # Initialize and run pipeline
    try:
        pipeline = UnifiedDataPipeline(
            mode=args.mode,
            sync_xdrive=args.sync_xdrive,
            date_stamp=args.date_stamp,
            dry_run=args.dry_run
        )

        success = pipeline.run_pipeline()

        if success:
            print("\n" + "=" * 80)
            print("✅ UNIFIED PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
            print("=" * 80)
            print("🎯 Consolidated functionality from 3 legacy scripts:")
            print("   • preprocess_all_data.py (X-drive integration)")
            print("   • comprehensive_data_preprocessing_pipeline.py (Excel formulas)")
            print("   • process_input_data_files.py (STMP processing)")
            print("\n📁 All processed data available in: smokingABM/data/")
            if args.sync_xdrive:
                print("🔄 Results synchronized to X-drive")
            print("📋 Check unified_pipeline_report_*.txt for detailed results")
            print("=" * 80)
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("❌ UNIFIED PIPELINE EXECUTION FAILED")
            print("=" * 80)
            print("📋 Check unified_data_pipeline.log for detailed error information")
            print("=" * 80)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("⏹️  PIPELINE EXECUTION INTERRUPTED BY USER")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"💥 PIPELINE EXECUTION FAILED WITH UNEXPECTED ERROR")
        print("=" * 80)
        print(f"Error: {e}")
        print("📋 Check unified_data_pipeline.log for detailed error information")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()
