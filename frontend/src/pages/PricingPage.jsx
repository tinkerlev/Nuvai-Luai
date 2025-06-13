// src/pages/PricingPage.jsx

import React from 'react';
import { useStripe } from '@stripe/react-stripe-js';
import { useAuth } from '../constants/AuthContext';
import { useNavigate } from 'react-router-dom';

const PricingPage = () => {
  const stripe = useStripe();
  const { user } = useAuth();
  const navigate = useNavigate();

  const soloFreePriceId = process.env.REACT_APP_STRIPE_PRICE_ID_SOLO_FREE;
  const soloMonthlyPriceId = process.env.REACT_APP_STRIPE_PRICE_ID_SOLO_MONTHLY;
  const soloYearlyPriceId = process.env.REACT_APP_STRIPE_PRICE_ID_SOLO_YEARLY;
  const proBusinessPriceId = process.env.REACT_APP_STRIPE_PRICE_ID_PRO_BUSINESS;

  const handleSubscription = async (priceId) => {
    if (!user) {
      navigate('/login');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ priceId: priceId })
      });

      const session = await response.json();
      if (response.status !== 200) {
        throw new Error(session.error || "Failed to create session.");
      }

      const { error } = await stripe.redirectToCheckout({
        sessionId: session.id,
      });

      if (error) {
        console.error("Stripe checkout error:", error.message);
      }
    } catch (error) {
      console.error("Subscription failed:", error.message);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-8">
      <h1 className="text-4xl font-bold text-center mb-12">Choose Your Plan</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-8 items-start">
        {/* Basic Plan */}
        <div className="border rounded-lg p-6 w-full max-w-sm mx-auto text-center">
          <h2 className="text-2xl font-semibold">Basic Plan for Free</h2>
          <p className="text-4xl font-bold my-4">$0.00<span className="text-xl">/mo</span></p>
          <p className="text-gray-500 mb-4">Start scanning with zero commitment</p>
          <ul className="text-sm text-left mb-6 space-y-2">
            <li>✔ 1 AI-powered scan per month</li>
            <li>✔ No export or PDF reporting</li>
            <li>✔ Limited rule sets (basic checks only)</li>
            <li>✔ Great for testing and learning</li>
            <li>✔ No credit card required</li>
          </ul>
          <button 
            onClick={() => handleSubscription(soloFreePriceId)} 
            className="btn btn-primary w-full"
            disabled={!stripe}
          >
            Choose Plan
          </button>
        </div>

        <div className="border rounded-lg p-6 w-full max-w-sm mx-auto text-center border-primary shadow-lg">
          <h2 className="text-2xl font-semibold">Solo Monthly</h2>
          <p className="text-4xl font-bold my-4">$19<span className="text-xl">/mo</span></p>
          <p className="text-gray-500 mb-4">Best for individual developers</p>
          <ul className="text-sm text-left mb-6 space-y-2">
            <li>✔ Unlimited scans every month</li>
            <li>✔ Access to all vulnerability engines</li>
            <li>✔ Downloadable PDF reports or HTML</li>
            <li>✔ Priority updates with new detection rules</li>
            <li>✔ Designed for freelance developers & pentesters</li>
          </ul>
          <button 
            onClick={() => handleSubscription(soloMonthlyPriceId)} 
            className="btn btn-primary w-full"
            disabled={!stripe}
          >
            Choose Plan
          </button>
        </div>

        <div className="border rounded-lg p-6 w-full max-w-sm mx-auto text-center border-primary shadow-lg">
          <h2 className="text-2xl font-semibold">Solo Yearly</h2>
          <p className="text-sm text-primary">SAVE 15%</p>
          <p className="text-4xl font-bold my-4">$190<span className="text-xl">/yr</span></p>
          <p className="text-gray-500 mb-4">Most Chosen ⭐️</p>
          <p className="text-gray-500 mb-4">Annual plan with 1 month free</p>
          <ul className="text-sm text-left mb-6 space-y-2">
            <li>✔ All features of Solo Yearly</li>
            <li>✔ Pay once, use all year</li>
            <li>✔ 1 free month included (save $38)</li>
            <li>✔ Locked-in pricing for 12 months</li>
            <li>✔ No renewal surprises or hidden fees</li>
          </ul>
          <button 
            onClick={() => handleSubscription(soloYearlyPriceId)}
            className="btn btn-primary w-full"
            disabled={!stripe}
          >
            Choose Plan
          </button>
        </div>

        <div className="border rounded-lg p-6 w-full max-w-sm mx-auto text-center border-primary shadow-lg">
          <h2 className="text-2xl font-semibold">PRO Business</h2>
          <p className="text-4xl font-bold my-4">$250<span className="text-xl">/mo</span></p>
          <p className="text-gray-500 mb-4">For teams and secure development</p>
          <ul className="text-sm text-left mb-6 space-y-2">
            <li>✔ Unlimited scans for your Business</li>
            <li>✔ Shared dashboard for teams</li>
            <li>✔ Advanced analytics and custom export</li>
            <li>✔ Audit-ready PDF reports</li>
            <li>✔ PDF reports suitable for ISO/NIST audits</li>
            <li>✔ Priority SLA support (48h guaranteed)</li>
            <li>✔ 2 free months with annual billing</li>
            <li>✔ Integrations: GitHub, GitLab, Bitbucket (coming soon)</li>
          </ul>
          <button 
            onClick={() => handleSubscription(proBusinessPriceId)}
            className="btn btn-primary w-full"
            disabled={!stripe}
          >
            Choose Plan
          </button>
        </div>

      </div>
    </div>
  );
};

export default PricingPage;
