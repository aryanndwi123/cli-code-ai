#!/usr/bin/env node

import { authClient } from './dist/cli/auth.js';

async function testCliAuth() {
    console.log('🔐 Testing CLI Authentication Client\n');

    try {
        console.log('=== Testing User Signup ===');
        const signupResult = await authClient.signup({
            email: 'cli-test@example.com',
            password: 'TestPass1!',
            username: 'cliuser'
        });

        if (signupResult.data) {
            console.log('✅ CLI Signup successful!');
            console.log(`   User: ${signupResult.data.email}`);
        } else {
            console.log('❌ CLI Signup failed:', signupResult.error);
        }

        console.log('\n=== Testing User Signin ===');
        const signinResult = await authClient.signin({
            email: 'cli-test@example.com',
            password: 'TestPass1!'
        });

        if (signinResult.data?.access_token) {
            console.log('✅ CLI Signin successful!');
            console.log(`   Token type: ${signinResult.data.token_type}`);
            console.log(`   Expires in: ${signinResult.data.expires_in} seconds`);

            console.log('\n=== Testing Get Profile ===');
            const profileResult = await authClient.getProfile();

            if (profileResult.data) {
                console.log('✅ CLI Profile retrieval successful!');
                console.log(`   User: ${profileResult.data.email}`);
                console.log(`   Username: ${profileResult.data.username}`);
            } else {
                console.log('❌ CLI Profile retrieval failed:', profileResult.error);
            }

            console.log('\n=== Testing Token Verification ===');
            const isAuthenticated = await authClient.verifyToken();
            console.log(`✅ Token verification: ${isAuthenticated ? 'Valid' : 'Invalid'}`);

            console.log('\n=== Testing Authentication Status ===');
            const authStatus = await authClient.isAuthenticated();
            console.log(`✅ Authentication status: ${authStatus ? 'Authenticated' : 'Not authenticated'}`);

            console.log('\n=== Testing API Key Refresh ===');
            const apiKeyResult = await authClient.refreshApiKey();

            if (apiKeyResult.data?.api_key) {
                console.log('✅ CLI API key refresh successful!');
                console.log(`   New API key: ${apiKeyResult.data.api_key.substring(0, 10)}...`);
            } else {
                console.log('❌ CLI API key refresh failed:', apiKeyResult.error);
            }

            console.log('\n=== Testing Logout ===');
            const logoutResult = await authClient.logout();

            if (logoutResult.status === 200) {
                console.log('✅ CLI Logout successful!');
            } else {
                console.log('❌ CLI Logout failed:', logoutResult.error);
            }

        } else {
            console.log('❌ CLI Signin failed:', signinResult.error);
            return;
        }

        console.log('\n🎉 All CLI authentication tests completed!');

    } catch (error) {
        console.error('❌ CLI Auth test failed with exception:', error.message);
    }
}

// Run the test
testCliAuth();