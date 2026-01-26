"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Github } from "lucide-react";

export default function Header() {
  return (
    <header className="border-b border-border-subtle bg-bg-primary">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-xl font-bold text-text-primary">SpendLens</span>
        </Link>
        <nav className="flex items-center space-x-2 md:space-x-4">
          <Button variant="ghost" size="sm" asChild className="hidden sm:flex">
            <Link href="https://github.com" target="_blank" rel="noopener noreferrer">
              <Github className="h-4 w-4 md:mr-2" />
              <span className="hidden md:inline">GitHub</span>
            </Link>
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/about">About</Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}

