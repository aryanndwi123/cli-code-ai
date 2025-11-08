#!/usr/bin/env node

import { program } from 'commander';
import chalk from 'chalk';
import boxen from 'boxen';
import inquirer from 'inquirer';
import ora from 'ora';
import { authClient } from './auth';
import { LoginCredentials, SignupCredentials } from '@/types/auth';

// CLI metadata
const version = '1.0.0';
const title = chalk.cyan.bold('Claude Code');
const subtitle = chalk.gray('AI-powered development assistant');

// Welcome message
function showWelcome() {
  console.log(
    boxen(`${title}\n${subtitle}`, {
      padding: 1,
      margin: 1,
      borderStyle: 'round',
      borderColor: 'cyan'
    })
  );
}

// Error handler
function handleError(error: string) {
  console.error(chalk.red('❌ Error:'), error);
  process.exit(1);
}

// Success message
function showSuccess(message: string) {
  console.log(chalk.green('✅'), message);
}

// Setup main program
program
  .name('claude-code')
  .description('AI-powered development assistant')
  .version(version, '-v, --version', 'Display version number')
  .option('-q, --quiet', 'Suppress non-essential output')
  .hook('preAction', (thisCommand) => {
    if (!thisCommand.opts().quiet && thisCommand.name() !== 'help') {
      showWelcome();
    }
  });

// Authentication commands
const authProgram = program
  .command('auth')
  .description('Authentication commands');

authProgram
  .command('signup')
  .description('Create a new account')
  .action(async () => {
    try {
      const answers = await inquirer.prompt<SignupCredentials>([
        {
          type: 'input',
          name: 'email',
          message: 'Email:',
          validate: (input: string) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(input) || 'Please enter a valid email address';
          }
        },
        {
          type: 'input',
          name: 'username',
          message: 'Username (optional):'
        },
        {
          type: 'password',
          name: 'password',
          message: 'Password:',
          mask: '*',
          validate: (input: string) => {
            return input.length >= 6 || 'Password must be at least 6 characters';
          }
        },
        {
          type: 'password',
          name: 'confirmPassword',
          message: 'Confirm Password:',
          mask: '*',
          validate: (input: string, answers?: any) => {
            return input === answers?.password || 'Passwords do not match';
          }
        }
      ]);

      // Remove confirmPassword before sending to API
      const { confirmPassword, ...credentials } = answers;

      const spinner = ora('Creating account...').start();

      const response = await authClient.signup(credentials);

      spinner.stop();

      if (response.error) {
        handleError(response.error);
      } else {
        showSuccess('Account created successfully!');
        console.log(chalk.blue('💡 Run'), chalk.cyan('claude-code auth signin'), chalk.blue('to sign in'));
      }
    } catch (error: any) {
      handleError(error.message);
    }
  });

authProgram
  .command('signin')
  .description('Sign into your account')
  .action(async () => {
    try {
      // Check if already authenticated
      if (await authClient.isAuthenticated()) {
        const profile = await authClient.getProfile();
        if (profile.data) {
          console.log(chalk.green('✅ Already signed in as'), chalk.cyan(profile.data.email));
          return;
        }
      }

      const credentials = await inquirer.prompt<LoginCredentials>([
        {
          type: 'input',
          name: 'email',
          message: 'Email:'
        },
        {
          type: 'password',
          name: 'password',
          message: 'Password:',
          mask: '*'
        }
      ]);

      const spinner = ora('Signing in...').start();

      const response = await authClient.signin(credentials);

      spinner.stop();

      if (response.error) {
        handleError(response.error);
      } else {
        showSuccess('Successfully signed in!');
      }
    } catch (error: any) {
      handleError(error.message);
    }
  });

authProgram
  .command('logout')
  .description('Sign out of your account')
  .action(async () => {
    try {
      const spinner = ora('Signing out...').start();

      await authClient.logout();

      spinner.stop();
      showSuccess('Successfully signed out!');
    } catch (error: any) {
      handleError(error.message);
    }
  });

authProgram
  .command('status')
  .description('Check authentication status')
  .action(async () => {
    try {
      const spinner = ora('Checking status...').start();

      const isAuth = await authClient.isAuthenticated();

      if (isAuth) {
        const profile = await authClient.getProfile();
        spinner.stop();

        if (profile.data) {
          console.log(chalk.green('✅ Signed in as:'), chalk.cyan(profile.data.email));
          console.log(chalk.gray('Member since:'), new Date(profile.data.created_at).toLocaleDateString());
          if (profile.data.last_login) {
            console.log(chalk.gray('Last login:'), new Date(profile.data.last_login).toLocaleString());
          }
        }
      } else {
        spinner.stop();
        console.log(chalk.red('❌ Not signed in'));
        console.log(chalk.blue('💡 Run'), chalk.cyan('claude-code auth signin'), chalk.blue('to sign in'));
      }
    } catch (error: any) {
      handleError(error.message);
    }
  });

authProgram
  .command('refresh-key')
  .description('Refresh your API key')
  .action(async () => {
    try {
      if (!(await authClient.isAuthenticated())) {
        handleError('Please sign in first');
      }

      const { confirmed } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'confirmed',
          message: 'This will invalidate your current API key. Continue?',
          default: false
        }
      ]);

      if (!confirmed) {
        console.log(chalk.yellow('🚫 Operation cancelled'));
        return;
      }

      const spinner = ora('Refreshing API key...').start();

      const response = await authClient.refreshApiKey();

      spinner.stop();

      if (response.error) {
        handleError(response.error);
      }
    } catch (error: any) {
      handleError(error.message);
    }
  });

// Configuration commands
program
  .command('config')
  .description('Configuration management')
  .option('--set-api-url <url>', 'Set the API URL')
  .option('--show', 'Show current configuration')
  .action(async (options) => {
    if (options.setApiUrl) {
      authClient.setApiUrl(options.setApiUrl);
    } else if (options.show) {
      const config = authClient.getConfig();
      console.log(chalk.blue('Current configuration:'));
      console.log(JSON.stringify(config, null, 2));
    } else {
      console.log(chalk.yellow('Please specify an option. Use --help for more information.'));
    }
  });

// Main chat command (placeholder)
program
  .command('chat')
  .description('Start an interactive chat session with Claude')
  .action(async () => {
    if (!(await authClient.isAuthenticated())) {
      handleError('Please sign in first with: claude-code auth signin');
    }

    console.log(chalk.blue('🤖 Starting Claude Code chat session...'));
    console.log(chalk.gray('(This feature is coming soon!)'));
  });

// Error handling
program.exitOverride();

try {
  program.parse();
} catch (err: any) {
  if (err.code === 'commander.helpDisplayed') {
    process.exit(0);
  }
  handleError(err.message);
}

// Show help if no command provided
if (process.argv.length <= 2) {
  showWelcome();
  program.outputHelp();
}