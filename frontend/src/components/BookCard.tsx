import { Card, CardContent} from "@/components/ui/card";
import { BookOpen } from "lucide-react";

interface BookCardProps {
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
  snippet?: string; // pour le preview / best chunk
  best_chunk_preview?: string;
  pdfUrl:string;
}
 
/*

const BookCard = ({ title, authors, imageLinks, publishedDate, isbn,pdfUrl }: BookCardProps) => {
  console.log(pdfUrl);
  
  return (
    <Card className="group overflow-hidden transition-all duration-300 hover:shadow-elegant hover:-translate-y-1 bg-card border-border">
      <CardContent className="p-0">
        <div className="aspect-[2/3] relative overflow-hidden bg-secondary cursor-pointer"
       onClick={() => {
  if (pdfUrl) {
    window.open(`http://localhost:5000/pdf/${pdfUrl}`, "_blank");
  }
}}
       >
          {imageLinks ? (
            <img
              src={imageLinks?.thumbnail}
              alt={title}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-subtle">
              <BookOpen className="h-16 w-16 text-muted-foreground" />
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-background/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>
        <div className="p-4 space-y-2">
          <h3 className="font-semibold text-lg line-clamp-2 text-card-foreground">
            {title}
          </h3>
          <p className="text-sm text-muted-foreground line-clamp-1">
           {authors && authors.length > 0 ? authors.join(", ") : "Author unknown"}
          </p>
          {publishedDate && (
            <p className="text-xs text-muted-foreground">
              Published in {publishedDate}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default BookCard;
*/
import { useState } from "react";
import BookPreviewModal from "./ui/BookPreviewModal";

const BookCard = ({ title, authors, imageLinks, publishedDate, pdfUrl }: BookCardProps) => {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Card
        className="group overflow-hidden transition-all duration-300 hover:shadow-elegant hover:-translate-y-1 bg-card border-border cursor-pointer"
        onClick={() => setOpen(true)}
      >
        <CardContent className="p-0">
          <div className="aspect-[2/3] relative overflow-hidden bg-secondary">
            {imageLinks ? (
              <img
                src={imageLinks?.thumbnail}
                alt={title}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gradient-subtle">
                <BookOpen className="h-16 w-16 text-muted-foreground" />
              </div>
            )}
          </div>

          <div className="p-4 space-y-2">
            <h3 className="font-semibold text-lg line-clamp-2">{title}</h3>
            <p className="text-sm text-muted-foreground line-clamp-1">
              {authors?.length ? authors.join(", ") : "Author unknown"}
            </p>
            {publishedDate && (
              <p className="text-xs text-muted-foreground">
                Publié en {publishedDate}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Modal */}
      <BookPreviewModal
        open={open}
        onClose={() => setOpen(false)}
        title={title}
        authors={authors || []}
        publishedDate={publishedDate}
        image={imageLinks?.thumbnail}
        pdfUrl={pdfUrl}
      />
    </>
  );
};
export default BookCard;

