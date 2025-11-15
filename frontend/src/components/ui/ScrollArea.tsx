import * as React from "react";
import * as ScrollAreaPrimitive from "@radix-ui/react-scroll-area";
import { cn } from "@/lib/utils";

export interface ScrollAreaProps
  extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
  dir?: "ltr" | "rtl";
}

export const ScrollArea = React.forwardRef<HTMLDivElement, ScrollAreaProps>(
  ({ className, children, dir = "ltr", ...props }, ref) => (
    <ScrollAreaPrimitive.Root
      dir={dir}
      className={cn("relative overflow-hidden", className)}
      {...props}
    >
      <ScrollAreaPrimitive.Viewport
        className="h-full w-full rounded-lg"
        ref={ref}
      >
        {children}
      </ScrollAreaPrimitive.Viewport>

      <ScrollAreaPrimitive.Scrollbar
        orientation="vertical"
        className="flex touch-none select-none p-0.5 transition-colors duration-150 ease-out data-[state=hidden]:opacity-0"
      >
        <ScrollAreaPrimitive.Thumb
          className="relative flex-1 rounded-full bg-accent hover:bg-accent-foreground"
        />
      </ScrollAreaPrimitive.Scrollbar>

      <ScrollAreaPrimitive.Scrollbar
        orientation="horizontal"
        className="flex h-2.5 touch-none select-none p-0.5 data-[state=hidden]:opacity-0"
      >
        <ScrollAreaPrimitive.Thumb
          className="relative flex-1 rounded-full bg-accent hover:bg-accent-foreground"
        />
      </ScrollAreaPrimitive.Scrollbar>

      <ScrollAreaPrimitive.Corner className="bg-accent" />
    </ScrollAreaPrimitive.Root>
  )
);

ScrollArea.displayName = "ScrollArea";
