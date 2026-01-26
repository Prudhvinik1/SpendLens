import Link from "next/link";
import { Wallet } from "lucide-react";

interface HeaderProps {
  showActions?: boolean;
}

export function Header({ showActions = false }: HeaderProps) {
  return (
    <header className="border-b border-border-subtle bg-bg-primary/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-accent-orange/10 flex items-center justify-center">
            <Wallet className="w-5 h-5 text-accent-orange" />
          </div>
          <span className="text-xl font-semibold text-text-primary">
            SpendLens
          </span>
        </Link>

        {showActions && (
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="text-sm text-text-secondary hover:text-text-primary transition-colors"
            >
              Upload New
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}
