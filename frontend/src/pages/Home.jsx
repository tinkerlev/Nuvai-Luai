// file: Home.jsx

import React from "react";
import { Icon } from '@iconify/react';
import { motion } from "framer-motion";
import { Link } from "react-router-dom";

// Animation variants
const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6 }
  }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
};

const pulseAnimation = {
  scale: [1, 1.05, 1],
  transition: { 
    duration: 1.5, 
    repeat: Infinity,
    ease: "easeInOut" 
  }
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-base-100 text-base-content">
  
      
      {/* Hero Section with Animation */}
      <header className="hero py-16 md:py-24 mb-12">
        <motion.div 
          className="hero-content text-center"
          initial="hidden"
          animate="visible"
          variants={fadeIn}
        >
          <div className="max-w-3xl">
            <motion.h1
              className="text-4xl md:text-5xl font-bold mb-6 leading-tight bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"
              variants={fadeIn}
            >
              Sometimes just one little mistake in your code can cause real problems! and you won’t notice it until it’s too late
            </motion.h1>
            <motion.p 
              className="text-lg md:text-xl mb-8"
              variants={fadeIn}
            >
                Luai helps you spot the risky parts in your code, before someone else does. It doesn’t matter if you built it with AI, no-code tools, or your own hands, it’s just here to keep you safe.
            </motion.p>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Link to="/early-access" className="btn btn-primary btn-lg shadow-lg">
              Get Early Access
              </Link>
            </motion.div>
            <motion.p 
              className="text-sm mt-3 text-base-content/70"
              variants={fadeIn}
            >
              Free signup – early access is limited.
            </motion.p>
          </div>
        </motion.div>
      </header>

      {/* About Section */}
      <motion.section 
        className="max-w-3xl mx-auto px-4 text-center mb-24"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={fadeIn}
      >
        <div className="card bg-base-200 shadow-xl border border-base-300">
          <div className="card-body p-8">
            <motion.h2 
              className="card-title text-2xl md:text-3xl font-bold justify-center mb-6"
              variants={fadeIn}
            >
              What is Luai?
            </motion.h2>
            <motion.p 
              className="text-base md:text-lg leading-relaxed"
              variants={fadeIn}
            >
              Working on something new? Maybe you used AI, a no-code tool <br />
              Or maybe you're a hands-on developer who writes clean code with thoughtful comments.
              <br className="hidden md:block" />
              Before you share it with the world. let <strong className="text-primary">Luai</strong> help make sure it's safe.
            </motion.p>
            <motion.p 
              className="mt-6 text-base md:text-lg"
              variants={fadeIn}
            >
              <strong className="text-primary">Luai</strong>  is a helpful security tool that looks through your code with a fresh set of eyes 
              It gets what you're trying to build, finds things that might cause trouble, even if they’re just hidden in your comments.  
              It’s like having a teammate who sees the stuff you might miss.
            </motion.p>
            <motion.div 
              className="alert alert-info mt-8 shadow-md"
              variants={fadeIn}
            >
              <Icon icon="mdi:information" className="h-6 w-6 flex-shrink-0" />
              <span>Behind the scenes, <strong className="text-primary">Luai</strong> quietly checks your code for risky patterns, small mistakes, and things that don’t look quite right, even if they seem fine at first glance.</span>
            </motion.div>
          </div>
        </div>
      </motion.section>

      {/* Benefits Section */}
      <motion.section 
        className="max-w-4xl mx-auto px-4 mb-24"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={staggerContainer}
      >
        <motion.h2 
          className="text-2xl md:text-3xl font-bold text-center mb-10"
          variants={fadeIn}
        >
          Who is Luai for?
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { icon: "mdi:code", text: "Builders using AI or No-Code platforms" },
            { icon: "ix:ai", text: "Developers who want peace of mind" },
            { icon: "mdi:shield-check", text: "Teams aiming for ISO, NIST, and OWASP compliance" },
            { icon: "mdi:security", text: "Anyone who wants to catch security flaws early" },
            { icon: "mdi:school", text: "Students who want to write safer code and learn as they go" },
            { icon: "mdi:teach", text: "Teachers who want to show best practices in real time" }

          ].map((item, index) => (
            <motion.div 
              key={index}
              className="card bg-base-200 hover:bg-base-300 transition-colors duration-300 shadow-lg"
              variants={fadeIn}
              whileHover={{ y: -5 }}
            >
              <div className="card-body">
                <div className="flex items-center gap-3">
                  <div className="bg-primary/10 p-3 rounded-full">
                    <Icon icon={item.icon} className="text-primary text-2xl" />
                  </div>
                  <span className="text-lg font-medium">{item.text}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Key Features Section */}
      <motion.section 
        className="max-w-4xl mx-auto px-4 mb-24 py-12 bg-base-200 rounded-box shadow-inner"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={staggerContainer}
      >
        <motion.h2 
          className="text-2xl md:text-3xl font-bold text-center mb-10"
          variants={fadeIn}
        >
          Key Features
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-8">
          {[
            { icon: "mdi:translate", text: "Supports multiple languages (Python, JavaScript, HTML, and more)" },
            { icon: "mdi:robot", text: "Uses AI to spot security risks automatically" },
            { icon: "mdi:comment-text", text: "Understands developer comments and context" },
            { icon: "mdi:lightbulb", text: "Gives clear suggestions on how to fix issues" },
            { icon: "mdi:file-export", text: "Lets you export reports in PDF, JSON, or HTML" },
            { icon: "mdi:check-circle", text: "Helps you stay aligned with ISO, NIST, and OWASP standards" },
            { icon: "mdi:clock-fast", text: "Detects issues early, before they become critical bugs" },
            { icon: "mdi:plug", text: "Simple integration upload code and get instant feedback" },
            { icon: "mdi:lock", text: "Privacy-first your code stays local or is processed securely" },
            { icon: "mdi:bug-check", text: "Highlights vulnerable code with severity levels for faster triage" }
          ].map((item, index) => (
            <motion.div 
              key={index} 
              className="flex items-start gap-3"
              variants={fadeIn}
            >
              <div className="bg-primary/20 p-2 rounded-full mt-1">
                <Icon icon={item.icon} className="text-primary text-xl" />
              </div>
              <span className="text-base md:text-lg">{item.text}</span>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Example Section */}
      <motion.section 
        className="max-w-3xl mx-auto px-4 mb-24"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={fadeIn}
      >
        <div className="card bg-gradient-to-br from-base-300 to-base-200 shadow-xl">
          <div className="card-body p-8">
            <motion.h2 
              className="card-title text-2xl font-bold justify-center mb-6"
              variants={fadeIn}
            >
              How does it work?
            </motion.h2>
            <div className="mockup-code shadow-lg bg-neutral text-neutral-content">
              <pre data-prefix="#"><code className="text-warning">✘ This is risky:</code></pre>
              <pre><code>eval(user_input)</code></pre>
              <pre data-prefix="#"><code className="text-success">✔ Luai warning: Code injection detected</code></pre>
            </div>
            <motion.div 
              className="alert alert-warning shadow-md mt-6"
              variants={fadeIn}
            >
              <Icon icon="mdi:alert" className="h-6 w-6" />
              <span>This code could open the door to harmful commands if misused.</span>
            </motion.div>
            <motion.div className="alert alert-success shadow-md mt-4" variants={fadeIn}>
              <Icon icon="mdi:check-circle" className="h-6 w-6" />
              <span>Luai catches it, explains the risk, and gives you a clear way to fix it.</span>
            </motion.div>
          </div>
        </div>
      </motion.section>

      {/* Final CTA */}
      <motion.section 
        className="text-center mb-24 px-4"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={fadeIn}
      >
        <div className="card bg-gradient-to-r from-primary/10 to-secondary/10 shadow-xl max-w-2xl mx-auto border border-base-300">
          <div className="card-body p-8">
            <motion.h2 
              className="card-title text-2xl md:text-3xl font-bold justify-center mb-6"
              variants={fadeIn}
            >
              Luai is almost ready
            </motion.h2>
            <motion.p 
              className="mb-6 text-lg"
              variants={fadeIn}
            >
              Want to be one of the first to try it? We're giving early access to a small group of people who care about writing safer code
            </motion.p>
            <motion.div 
              className="card-actions justify-center"
              variants={fadeIn}
              animate={pulseAnimation}
            >
              <Link to="/early-access" className="btn btn-primary btn-lg gap-2 shadow-lg">
                <Icon icon="mdi:rocket-launch" className="text-xl" />
                Get Early Access
              </Link>
            </motion.div>
            <motion.p 
              className="text-sm mt-3 text-base-content/70"
              variants={fadeIn}
            >
              No credit card needed. Just sign up, and we’ll let you know when it’s a live
            </motion.p>
          </div>
        </div>
      </motion.section>
    </div>
  );
}
