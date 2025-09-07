import click
import getpass
from .auth import AuthClient
from .config import Config

# Initialize auth client
auth = AuthClient()

@click.group()
@click.version_option(version="1.0.0")
def cli():
  
    pass

@cli.command()
def signup():
    """Register a new account"""
    click.echo(click.style("=== Sign Up ===", fg="blue", bold=True))
    
    email = click.prompt("Email", type=str).strip()
    if not email:
        click.echo(click.style(" Email cannot be empty", fg="red"))
        return
    
    password = getpass.getpass("Password: ")
    if not password:
        click.echo(click.style(" Password cannot be empty", fg="red"))
        return
    
    confirm_password = getpass.getpass("Confirm Password: ")
    if password != confirm_password:
        click.echo(click.style(" Passwords don't match", fg="red"))
        return
    
    with click.progressbar([1], label="Creating account") as bar:
        for _ in bar:
            success, message = auth.signup(email, password)
    
    if success:
        click.echo(click.style(f" {message}", fg="green"))
    else:
        click.echo(click.style(f" {message}", fg="red"))

@cli.command()
def signin():
    """Sign into your account"""
    click.echo(click.style("=== Sign In ===", fg="blue", bold=True))
    
    # Check if already logged in
    if auth.is_logged_in():
        success, profile = auth.get_profile()
        if success:
            click.echo(click.style(f" Already logged in as {profile['email']}", fg="green"))
            return
    
    email = click.prompt("Email", type=str).strip()
    if not email:
        click.echo(click.style(" Email cannot be empty", fg="red"))
        return
    
    password = getpass.getpass("Password: ")
    if not password:
        click.echo(click.style(" Password cannot be empty", fg="red"))
        return
    
    with click.progressbar([1], label="Signing in") as bar:
        for _ in bar:
            success, message = auth.signin(email, password)
    
    if success:
        click.echo(click.style(f" {message}", fg="green"))
    else:
        click.echo(click.style(f" {message}", fg="red"))

@cli.command()
def logout():
    """Log out of your account"""
    click.echo(click.style("=== Logout ===", fg="blue", bold=True))
    
    success, message = auth.logout()
    if success:
        click.echo(click.style(f" {message}", fg="green"))
    else:
        click.echo(click.style(f" {message}", fg="red"))

@cli.command()
def status():
    """Check login status"""
    success, data = auth.get_profile()
    if success:
        click.echo(click.style(f" Logged in as: {data['email']}", fg="green"))
        click.echo(f" Member since: {data['created_at']}")
    else:
        click.echo(click.style(f" Not logged in", fg="red"))

@cli.command()
def protected():
    """Example protected command"""
    success, data = auth.get_profile()
    if not success:
        click.echo(click.style(" Please sign in first", fg="red"))
        click.echo("Run: basault signin")
        return
    
    click.echo(click.style(f"🔒 Welcome to protected area, {data['email']}!", fg="green"))
    click.echo("🎉 You have access to premium features!")

@cli.command()
@click.option('--url', help='Set API URL')
def config(url):
    """Configure basault settings"""
    if url:
        Config.set_api_url(url)
        click.echo(click.style(f" API URL set to: {url}", fg="green"))
    else:
        current_url = Config.get_api_url()
        click.echo(f"Current API URL: {current_url}")

if __name__ == '__main__':
    cli()