"""
Command-line interface for AI Health Navigator.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

import click
import uvicorn
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from .core.config import settings
from .core.logging import get_logger
from .ai.models import model_manager
from .ai.llm_service import llm_service

console = Console()
logger = get_logger(__name__)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AI Health Navigator - Advanced AI-powered health navigation platform."""
    pass


@cli.command()
@click.option("--host", default=settings.api.host, help="Host to bind to")
@click.option("--port", default=settings.api.port, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--workers", default=1, help="Number of worker processes")
def serve(host: str, port: int, reload: bool, workers: int):
    """Start the AI Health Navigator API server."""
    console.print(Panel.fit(
        "[bold blue]AI Health Navigator[/bold blue]\n"
        "[dim]Advanced AI-powered health navigation platform[/dim]",
        border_style="blue"
    ))
    
    console.print(f"Starting server on [bold]{host}:{port}[/bold]")
    
    if reload:
        console.print("[yellow]Auto-reload enabled[/yellow]")
    
    try:
        uvicorn.run(
            "ai_health_navigator.api.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level=settings.monitoring.log_level.lower()
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Failed to start server: {e}[/red]")
        sys.exit(1)


@cli.command()
def init():
    """Initialize the AI Health Navigator system."""
    console.print(Panel.fit(
        "[bold green]Initializing AI Health Navigator[/bold green]\n"
        "Setting up AI models, LLM services, and configuration...",
        border_style="green"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Initialize AI models
        task = progress.add_task("Initializing AI models...", total=None)
        try:
            asyncio.run(model_manager.initialize_models())
            progress.update(task, description="✅ AI models initialized")
        except Exception as e:
            progress.update(task, description=f"❌ AI models failed: {e}")
            console.print(f"[red]Failed to initialize AI models: {e}[/red]")
            return
        
        # Initialize LLM service
        task = progress.add_task("Initializing LLM service...", total=None)
        try:
            asyncio.run(llm_service.initialize())
            progress.update(task, description="✅ LLM service initialized")
        except Exception as e:
            progress.update(task, description=f"❌ LLM service failed: {e}")
            console.print(f"[red]Failed to initialize LLM service: {e}[/red]")
            return
    
    console.print("\n[bold green]✅ Initialization completed successfully![/bold green]")


@cli.command()
def status():
    """Check the status of AI Health Navigator components."""
    console.print(Panel.fit(
        "[bold blue]AI Health Navigator Status[/bold blue]",
        border_style="blue"
    ))
    
    # Check AI models
    table = Table(title="AI Models Status")
    table.add_column("Model", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    for model_name, model in model_manager.models.items():
        status = "✅ Loaded" if model else "❌ Not loaded"
        details = f"Type: {type(model).__name__}"
        table.add_row(model_name, status, details)
    
    console.print(table)
    
    # Check LLM providers
    console.print("\n")
    table = Table(title="LLM Providers Status")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Model")
    
    try:
        health_status = asyncio.run(llm_service.health_check())
        for provider, is_healthy in health_status.items():
            status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
            model = settings.llm.default_model if provider == "openai" else "claude-3-sonnet"
            table.add_row(provider, status, model)
    except Exception as e:
        table.add_row("All", "❌ Error", str(e))
    
    console.print(table)


@cli.command()
@click.option("--symptoms", required=True, help="Patient symptoms description")
@click.option("--age", type=int, help="Patient age")
@click.option("--gender", help="Patient gender")
@click.option("--provider", help="Preferred LLM provider")
def analyze(symptoms: str, age: Optional[int], gender: Optional[str], provider: Optional[str]):
    """Analyze symptoms using the AI system."""
    console.print(Panel.fit(
        "[bold green]Symptom Analysis[/bold green]\n"
        f"[dim]Analyzing: {symptoms[:50]}{'...' if len(symptoms) > 50 else ''}[/dim]",
        border_style="green"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Analyzing symptoms...", total=None)
        
        try:
            # Perform analysis
            symptoms_analysis = asyncio.run(model_manager.analyze_symptoms(symptoms))
            
            # Perform LLM analysis
            llm_response = asyncio.run(llm_service.analyze_symptoms(
                symptoms=symptoms,
                age=age,
                gender=gender,
                provider=provider
            ))
            
            progress.update(task, description="✅ Analysis completed")
            
        except Exception as e:
            progress.update(task, description=f"❌ Analysis failed: {e}")
            console.print(f"[red]Analysis failed: {e}[/red]")
            return
    
    # Display results
    console.print("\n[bold]Analysis Results:[/bold]")
    
    # AI Model Results
    console.print("\n[bold cyan]AI Model Analysis:[/bold cyan]")
    console.print(f"Primary Symptoms: {', '.join(symptoms_analysis.primary_symptoms)}")
    console.print(f"Secondary Symptoms: {', '.join(symptoms_analysis.secondary_symptoms)}")
    console.print(f"Confidence: {symptoms_analysis.confidence_score:.2%}")
    console.print(f"Urgency Level: {symptoms_analysis.urgency_level.upper()}")
    console.print(f"Recommended Care: {symptoms_analysis.recommended_care}")
    
    # LLM Analysis
    console.print(f"\n[bold cyan]LLM Analysis ({llm_response.provider}):[/bold cyan]")
    console.print(Panel(llm_response.content, border_style="blue"))
    
    # Warnings
    if symptoms_analysis.urgency_level in ["high", "emergency"]:
        console.print("\n[bold red]⚠️  IMPORTANT WARNINGS:[/bold red]")
        console.print(f"[red]Urgency Level: {symptoms_analysis.urgency_level.upper()}[/red]")
        console.print(f"[red]Immediate Action: {symptoms_analysis.recommended_care}[/red]")


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Configuration file path")
def validate(config: Optional[str]):
    """Validate the system configuration."""
    console.print(Panel.fit(
        "[bold yellow]Configuration Validation[/bold yellow]",
        border_style="yellow"
    ))
    
    # Validate settings
    table = Table(title="Configuration Validation")
    table.add_column("Setting", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Value")
    
    # Check required settings
    required_settings = [
        ("Environment", settings.environment, True),
        ("API Host", settings.api.host, True),
        ("API Port", settings.api.port, True),
        ("Database URL", settings.database.url, True),
        ("Secret Key", settings.security.secret_key, True),
        ("OpenAI API Key", settings.llm.openai_api_key, False),
        ("Anthropic API Key", settings.llm.anthropic_api_key, False),
    ]
    
    all_valid = True
    for name, value, required in required_settings:
        if required and not value:
            status = "❌ Missing"
            all_valid = False
        elif value:
            status = "✅ Set"
        else:
            status = "⚠️  Optional"
        
        # Mask sensitive values
        display_value = value if not name.lower().endswith("key") else "***" if value else "Not set"
        table.add_row(name, status, str(display_value))
    
    console.print(table)
    
    if all_valid:
        console.print("\n[bold green]✅ Configuration is valid![/bold green]")
    else:
        console.print("\n[bold red]❌ Configuration has issues![/bold red]")
        console.print("Please check the missing required settings.")


@cli.command()
@click.option("--output", type=click.Path(), help="Output file path")
def export_config(output: Optional[str]):
    """Export the current configuration."""
    config_data = {
        "environment": settings.environment,
        "api": {
            "title": settings.api.title,
            "version": settings.api.version,
            "host": settings.api.host,
            "port": settings.api.port,
            "debug": settings.api.debug,
        },
        "database": {
            "url": settings.database.url,
            "pool_size": settings.database.pool_size,
        },
        "llm": {
            "default_model": settings.llm.default_model,
            "max_tokens": settings.llm.max_tokens,
            "temperature": settings.llm.temperature,
        },
        "monitoring": {
            "log_level": settings.monitoring.log_level,
            "enable_tracing": settings.monitoring.enable_tracing,
        }
    }
    
    if output:
        with open(output, 'w') as f:
            json.dump(config_data, f, indent=2)
        console.print(f"[green]Configuration exported to {output}[/green]")
    else:
        console.print(json.dumps(config_data, indent=2))


@cli.command()
@click.option("--model", required=True, help="Model name to test")
@click.option("--input", required=True, help="Test input")
def test_model(model: str, input: str):
    """Test a specific AI model."""
    console.print(Panel.fit(
        f"[bold blue]Testing Model: {model}[/bold blue]\n"
        f"[dim]Input: {input[:50]}{'...' if len(input) > 50 else ''}[/dim]",
        border_style="blue"
    ))
    
    try:
        if model == "symptom_classifier":
            result = asyncio.run(model_manager.analyze_symptoms(input))
            console.print("\n[bold green]Test Results:[/bold green]")
            console.print(f"Primary Symptoms: {result.primary_symptoms}")
            console.print(f"Confidence: {result.confidence_score:.2%}")
            console.print(f"Urgency Level: {result.urgency_level}")
        
        elif model == "llm":
            result = asyncio.run(llm_service.analyze_symptoms(input))
            console.print("\n[bold green]Test Results:[/bold green]")
            console.print(f"Provider: {result.provider}")
            console.print(f"Model: {result.model}")
            console.print(f"Tokens Used: {result.tokens_used}")
            console.print(Panel(result.content, border_style="blue"))
        
        else:
            console.print(f"[red]Unknown model: {model}[/red]")
            console.print("Available models: symptom_classifier, llm")
    
    except Exception as e:
        console.print(f"[red]Test failed: {e}[/red]")


@cli.command()
def health():
    """Perform a comprehensive health check."""
    console.print(Panel.fit(
        "[bold green]System Health Check[/bold green]",
        border_style="green"
    ))
    
    health_status = {}
    
    # Check AI models
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Checking AI models...", total=None)
        try:
            models_healthy = len(model_manager.models) > 0
            health_status["ai_models"] = models_healthy
            progress.update(task, description="✅ AI models checked")
        except Exception as e:
            health_status["ai_models"] = False
            progress.update(task, description=f"❌ AI models failed: {e}")
        
        # Check LLM providers
        task = progress.add_task("Checking LLM providers...", total=None)
        try:
            llm_health = asyncio.run(llm_service.health_check())
            health_status["llm_providers"] = llm_health
            progress.update(task, description="✅ LLM providers checked")
        except Exception as e:
            health_status["llm_providers"] = {"error": str(e)}
            progress.update(task, description=f"❌ LLM providers failed: {e}")
    
    # Display results
    table = Table(title="Health Check Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    # AI Models
    ai_status = "✅ Healthy" if health_status.get("ai_models") else "❌ Unhealthy"
    ai_details = f"{len(model_manager.models)} models loaded"
    table.add_row("AI Models", ai_status, ai_details)
    
    # LLM Providers
    llm_health = health_status.get("llm_providers", {})
    if isinstance(llm_health, dict) and "error" not in llm_health:
        healthy_providers = sum(llm_health.values())
        total_providers = len(llm_health)
        llm_status = "✅ Healthy" if healthy_providers > 0 else "❌ Unhealthy"
        llm_details = f"{healthy_providers}/{total_providers} providers healthy"
    else:
        llm_status = "❌ Error"
        llm_details = str(llm_health.get("error", "Unknown error"))
    
    table.add_row("LLM Providers", llm_status, llm_details)
    
    console.print(table)
    
    # Overall status
    overall_healthy = (
        health_status.get("ai_models", False) and 
        isinstance(llm_health, dict) and 
        "error" not in llm_health and 
        any(llm_health.values())
    )
    
    if overall_healthy:
        console.print("\n[bold green]✅ System is healthy![/bold green]")
    else:
        console.print("\n[bold red]❌ System has issues![/bold red]")


@cli.command()
@click.option("--format", "output_format", default="text", help="Output format (text, json)")
def info(output_format: str):
    """Display system information."""
    info_data = {
        "name": "AI Health Navigator",
        "version": "1.0.0",
        "description": "Advanced AI-powered health navigation platform",
        "environment": settings.environment,
        "api": {
            "host": settings.api.host,
            "port": settings.api.port,
            "debug": settings.api.debug,
        },
        "ai_models": list(model_manager.models.keys()),
        "llm_providers": list(llm_service.providers.keys()),
        "features": {
            "symptom_checker": settings.enable_symptom_checker,
            "provider_matching": settings.enable_provider_matching,
            "insurance_guidance": settings.enable_insurance_guidance,
            "multilingual": settings.enable_multilingual,
        }
    }
    
    if output_format == "json":
        console.print(json.dumps(info_data, indent=2))
    else:
        console.print(Panel.fit(
            f"[bold blue]{info_data['name']} v{info_data['version']}[/bold blue]\n"
            f"[dim]{info_data['description']}[/dim]",
            border_style="blue"
        ))
        
        table = Table(title="System Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in info_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    table.add_row(f"{key}.{sub_key}", str(sub_value))
            else:
                table.add_row(key, str(value))
        
        console.print(table)


if __name__ == "__main__":
    cli()
