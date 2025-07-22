# Grant AI - Phase 8 Integration Guide

This guide describes how to integrate and use the new modules added in Phase 8:

## Modules
- Impact Analysis (`src/grant_ai/analytics/impact_analysis.py`)
- Enhanced Proposal Generator (`src/grant_ai/proposal/enhanced_generator.py`)
- arXiv Monitor (`src/grant_ai/community/arxiv_monitor.py`)
- Mobile Accessibility (`src/grant_ai/mobile/accessibility.py`)
- Language Manager (`src/grant_ai/i18n/language_manager.py`)

## Integration Steps
1. Import the required modules in your workflow or CLI.
2. Use the provided classes and methods to analyze impact, generate proposals, monitor community signals, check mobile accessibility, and manage languages.
3. Run tests using `run.sh test-phase8` to validate integration.
4. Update configuration in `config/next_phase_config.yaml` as needed.

## Example Usage
See the test scripts in `tests/` for sample usage of each module.

## Troubleshooting
- Ensure all dependencies are installed and virtual environment is activated.
- Check for missing imports or function definitions in new modules.
- Refer to the test output log (`logs/test_output_phase8.log`) for results and errors.
