import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Value } from "@radix-ui/react-select";
import { useState } from "react";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
}


const SearchBar = ({ value, onChange, onSearch}: SearchBarProps) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      onSearch();
    }
  };




  return (
    <div className="relative w-full max-w-3xl mx-auto">
      <div className="relative flex items-center gap-2 bg-card border-2 border-border rounded-xl shadow-elegant transition-all duration-300 hover:shadow-xl focus-within:border-primary">
        <Input
          type="text"
          placeholder="Search for books by title, author, etc......"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          className="flex-1 border-0 bg-transparent text-lg py-6 px-6 focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground"
        />
        <Button
          onClick={onSearch}
          //onClick={() => SearchBooks(value)}
          className="mr-2 bg-[#964B00] hover:opacity-90 transition-opacity"
          size="lg"
        >
          <Search className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
};

export default SearchBar;
