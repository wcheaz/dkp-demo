import type { Metadata } from "next";

import { CopilotKit } from "@copilotkit/react-core";
import { LanguageProvider } from "@/i18n/language-provider";
import { defaultLocale } from "@/i18n/config";
import "./globals.css";
import "@copilotkit/react-ui/styles.css";

export const metadata: Metadata = {
  title: "Návrhový asistent",
  description: "Asistent pre návrh krovových konštrukcií",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang={defaultLocale} data-default-locale={defaultLocale}>
      <body className={"antialiased"}>
        <LanguageProvider>
          <CopilotKit
            runtimeUrl="/api/copilotkit"
            agent="my_agent"
            showDevConsole={process.env.NODE_ENV === "development"}
            enableInspector={process.env.NODE_ENV === "development"}
          >
            {children}
          </CopilotKit>
        </LanguageProvider>
      </body>
    </html>
  );
}
