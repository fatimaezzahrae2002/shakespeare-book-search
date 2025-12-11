import SearchBar from "./SearchBar";

interface HeroProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onSearch: () => void;
}

const Hero = ({ searchQuery, setSearchQuery, onSearch }: HeroProps) => {
  return (
    <section className="relative min-h-[60vh] flex items-center justify-center px-4 py-20 bg-gradient-subtle">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,hsl(38,92%,50%,0.1),transparent_50%)]" />
      <div className="relative z-10 w-full max-w-5xl mx-auto text-center space-y-12">
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <h1 className="text-5xl md:text-7xl font-bold bg-[#964B00] bg-clip-text text-transparent">
            Explore books by Shakespeare
          </h1>
         
        </div>
        <div className="animate-in fade-in slide-in-from-bottom-6 duration-700 delay-150">
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            onSearch={onSearch}
          />
        </div>
      </div>
    </section>
  );
};

export default Hero;
