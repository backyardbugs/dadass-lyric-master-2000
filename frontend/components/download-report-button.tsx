"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

type Props = {
  targetId: string;
  filename?: string;
  disabled?: boolean;
};

export function DownloadReportButton({ targetId, filename = "lyric-analysis-report.pdf", disabled }: Props) {
  const [exporting, setExporting] = useState(false);

  const onDownload = async () => {
    const el = document.getElementById(targetId);
    if (!el) return;
    setExporting(true);
    try {
      const html2pdf = (await import("html2pdf.js")).default;
      await html2pdf()
        .set({
          margin: [10, 10, 10, 10],
          filename,
          image: { type: "jpeg", quality: 0.92 },
          html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: "#09090b",
            logging: false,
          },
          jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
        } as Record<string, unknown>)
        .from(el)
        .save();
    } catch {
      /* user may have blocked download */
    } finally {
      setExporting(false);
    }
  };

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      className="border-zinc-600"
      disabled={disabled || exporting}
      onClick={onDownload}
    >
      {exporting ? "Building PDF…" : "Download report (PDF)"}
    </Button>
  );
}
