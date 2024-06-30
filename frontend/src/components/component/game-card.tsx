/**
* This code was generated by v0 by Vercel.
* @see https://v0.dev/t/Y6DM0o4IBmE
* Documentation: https://v0.dev/docs#integrating-generated-code-into-your-nextjs-app
*/

/** Add fonts into your Next.js project:

import { Inter } from 'next/font/google'

inter({
  subsets: ['latin'],
  display: 'swap',
})

To read more about using these font, please visit the Next.js documentation:
- App Directory: https://nextjs.org/docs/app/building-your-application/optimizing/fonts
- Pages Directory: https://nextjs.org/docs/pages/building-your-application/optimizing/fonts
**/
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export function GameCard({gameName, gameDescription}) {
   return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-center mb-2">{gameName}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center gap-4">
        <div className="px-4">
          <img
            src="/placeholder.svg"
            width={300}
            height={450}
            alt="Game Image"
            className="aspect-[2/3] object-cover rounded-lg"
          />
        </div>
        <div className="flex flex-col gap-4">
          <p className="text-center text-muted-foreground">{gameDescription}</p>
          <Button variant="default" className="bg-primary text-primary-foreground">
            Play Now
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

 const gameName = "Epic Adventure"
  const gameDescription =
    "Immerse yourself in an epic adventure through a vast open world, filled with dangerous foes, ancient mysteries, and a rich storyline that will keep you captivated for hours on end."