import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface BookPreviewModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  authors: string[];
  publishedDate?: string | number;
  image?: string;
  pdfUrl?: string;
}

const BookPreviewModal = ({
  open,
  onClose,
  title,
  authors,
  publishedDate,
  image,
  pdfUrl
}: BookPreviewModalProps) => {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">{title}</DialogTitle>
        </DialogHeader>

        <div className="flex gap-6">
          <img
            src={image}
            alt={title}
            className="w-48 h-72 rounded shadow-md object-cover"
          />

          <div className="flex flex-col gap-3">
            <p className="text-[#964B00]">
              {authors.join(', ')}
            </p>
            <p className="text-sm text-[#964B00]">
              Publié en : {publishedDate || "N/A"}
            </p>

            <Button
              className="mt-4 bg-[#964B00]"
              onClick={() => window.open(`http://localhost:5000/pdf/${pdfUrl}`, "_blank")}
            >
              📖 Lire le PDF
            </Button>

          </div>
        </div>

      </DialogContent>
    </Dialog>
  );
};

export default BookPreviewModal;
