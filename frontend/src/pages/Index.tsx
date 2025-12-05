import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Hero from "@/components/Hero";
import BookCard from "@/components/BookCard";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

interface Book {
  key?: string;
  title: string;
  authors?: string[];
  publishedDate?: string | number;
  isbn?: string[];
  cover_i?: number;
  imageLinks?: {
    thumbnail?: string;
    smallThumbnail?: string;
  };
  snippet?: string;
  best_chunk_preview?: string;
  pdfUrl:string;
}

const Index = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeQuery, setActiveQuery] = useState("");

  const {
    data: books = [],
    isLoading,
  } = useQuery({
    queryKey: ["books", activeQuery],
    queryFn: async () => {
      if (!activeQuery) return [];

      const response = await fetch(`http://localhost:5000/api/recherche`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ query: activeQuery }),
      });

      if (!response.ok) throw new Error("Erreur lors de la recherche");

      const data = await response.json();
      console.log("data",data);
      return data as Book[];
    },
    enabled: !!activeQuery,
  });

  const handleSearch = () => {
    if (!searchQuery.trim()) {
      toast.error("Veuillez entrer un terme de recherche");
      return;
    }
    setActiveQuery(searchQuery);
  };

  return (
    <div className="min-h-screen bg-background">
      <Hero
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onSearch={handleSearch}
      />

      <main className="container mx-auto px-4 py-12">
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {books.length > 0 && (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-foreground">
              Search results
              <span className="text-muted-foreground text-xl ml-3">
                ({books.length} books)
              </span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-6">
              {books.map((book) => (
                <BookCard
                  key={book.key}
                  title={book.title}
                  authors={book.authors || ["Author unknown"]}
                  imageLinks={book.imageLinks}   /* ✅ OBJET complet */
                  pdfUrl ={book.pdfUrl}
                />
              ))}
            </div>
          </div>
        )}

        {books.length === 0 && !isLoading && (
          <div className="text-center py-20">
            <p className="text-xl text-muted-foreground">
              No results found. Try another search.
            </p>
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;

