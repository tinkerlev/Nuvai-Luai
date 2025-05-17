import React from "react";
import { Link } from "react-router-dom";
import { Icon } from '@iconify/react';
import { motion } from "framer-motion";

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.6 }
  }
};

export default function Footer() {
  return (
    <motion.footer 
      className="footer footer-horizontal z-20 md:p-10 p-6 bg-base-200/60 text-base-content mt-auto border-t border-base-300"
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.2 }}
      variants={fadeIn}
    >
      <div className="flex-1">
        <div className="grid grid-flow-col gap-4">
          <Link to="/" className="link link-hover">Home</Link>
          <Link to="/about" className="link link-hover">About</Link>
          <Link to="/login" className="link link-hover">Login</Link>
          <Link to="/register" className="link link-hover">Register</Link>
        </div>
      </div> 
      
      <div className="flex-1 flex justify-center w-[fill-available]">
        <div className="flex gap-2">
          <a href="https://linkedin.com/company/Luai" target="_blank" rel="noreferrer" className="btn btn-ghost btn-sm btn-circle">
            <Icon icon="mdi:linkedin" className="h-5 w-5" />
          </a> 
          <a href="https://twitter.com/Luai_app" target="_blank" rel="noreferrer" className="btn btn-ghost btn-sm btn-circle">
            <Icon icon="mdi:twitter" className="h-5 w-5" />
          </a> 
          <a href="https://github.com/Luai" target="_blank" rel="noreferrer" className="btn btn-ghost btn-sm btn-circle">
            <Icon icon="mdi:github" className="h-5 w-5" />
          </a>
        </div>
      </div> 
      
      <div className="flex-1 flex justify-end w-[fill-available] text-right">
        <div>
          <p className="text-sm">
            Have questions? Email us at <a href="mailto:security@Luai.io" className="link link-primary">security@Luai.io</a>
          </p>
          <p className="text-xs mt-1">
            Copyright © {new Date().getFullYear()} - Luai Security Technologies
          </p>
        </div>
      </div>
    </motion.footer>
  );
}
