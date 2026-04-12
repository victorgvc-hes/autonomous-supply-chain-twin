# Contributing Guidelines

Thank you for your interest in contributing to this project.

This repository was developed as an end-to-end AI-powered supply chain analytics project focused on demand forecasting, digital twin simulation, and inventory optimisation. Contributions, suggestions, and improvements are welcome.

## How to Contribute

If you would like to contribute, please follow these guidelines:

1. Fork the repository
2. Create a dedicated feature branch
3. Make your changes
4. Test your changes locally
5. Submit a pull request with a clear and concise description

## Contribution Areas

Potential contribution areas include:

- data preprocessing and feature engineering improvements
- forecasting model development and comparison
- simulation and digital twin enhancements
- reinforcement learning experiments for inventory control
- evaluation metrics and benchmarking improvements
- reproducibility and project structure improvements
- visualization, reporting, and dashboard extensions
- documentation and usage examples

## Coding Standards

Please follow these basic rules:

- Write clear, readable, and modular Python code
- Prefer reusable functions and source modules over duplicated notebook logic
- Use meaningful names for files, variables, functions, and classes
- Add comments where the logic is not immediately obvious
- Keep notebooks, scripts, and source folders well organized
- Maintain consistency with the existing project structure

## Testing

Before submitting changes, make sure that:

- notebooks and scripts run correctly from the project root
- file paths and imports remain consistent
- outputs are reproducible where applicable
- no raw data, large model files, or unnecessary artifacts are committed
- relevant documentation is updated
- the end-to-end forecasting and simulation workflow is not broken

## Data Usage

This project uses the M5 Forecasting dataset from Kaggle.

Due to dataset licensing and repository size considerations:

- raw Kaggle data must not be committed to the repository
- processed datasets should remain local unless explicitly needed
- large outputs, cached files, and trained artifacts should not be pushed unless necessary
- contributors should follow the setup and download instructions provided in the README

## Project Scope

This repository is primarily focused on:

- intermittent demand forecasting
- multi-model evaluation
- inventory policy optimisation
- digital twin simulation
- supply chain analytics and decision support

Please keep contributions aligned with the core purpose of the project.

## Pull Request Notes

When opening a pull request, please include:

- a short summary of the change
- why the change improves the project
- any impact on forecasts, simulations, reports, or outputs
- any new dependencies, assumptions, or setup steps

## Questions or Suggestions

If you would like to suggest an improvement, feel free to open an issue or submit a pull request.