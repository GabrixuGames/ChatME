import React from "react";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";

interface SidebarPopoverProps {
  icon: React.ReactNode;
  children: React.ReactNode;
  label: string;
}

export const SidebarPopover: React.FC<SidebarPopoverProps> = ({ icon, children, label }) => {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button className="flex items-center justify-center w-10 h-10 rounded hover:bg-sidebar-accent focus:outline-none" aria-label={label}>
          {icon}
        </button>
      </PopoverTrigger>
      <PopoverContent
        side="right"
        align="start"
        className="min-w-[220px] p-2 bg-sidebar text-sidebar-foreground border-sidebar-border border shadow-lg rounded-lg"
      >
        {children}
      </PopoverContent>
    </Popover>
  );
};
