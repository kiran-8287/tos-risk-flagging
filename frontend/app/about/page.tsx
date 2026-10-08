export default function AboutPage() {
  return (
    <div className="py-16 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl">
          <h1 className="text-3xl font-semibold mb-6">How it works</h1>

          <div className="prose prose-slate max-w-none space-y-8">
            <section>
              <h2 className="text-xl font-semibold mb-4">Methodology</h2>
              <p className="text-muted-foreground">
                Upload a Terms of Service or Privacy Policy document. The system breaks it into
                individual clauses and classifies each one as Safe, Neutral, or Risky using a
                machine learning model trained on real-world clauses.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold mb-4">Features</h2>
              <p className="text-muted-foreground">
                Clause-level analysis, document-level risk summaries, and support for PDF, DOCX,
                and TXT files.
              </p>
            </section>

            <section className="rounded-lg border border-border bg-secondary/30 p-6">
              <h2 className="text-xl font-semibold mb-4">Important disclaimer</h2>
              <p className="text-muted-foreground">
                This is an educational screening tool and does not provide legal advice.
                The analysis is automated and may not capture all nuances of legal documents.
                Always consult a qualified legal professional for legal matters.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
