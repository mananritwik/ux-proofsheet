// Fixture: trimmed get_design_context output (React + Tailwind) for the Home hero
// and disputes card. Hand-written for ux-proofsheet tests.
export default function Home() {
  return (
    <div className="flex flex-col gap-[16px] px-[16px] pt-[12px] pb-[16px]" data-node-id="575:4610">
      <div className="flex flex-col gap-[4px] p-[14px] rounded-[12px] bg-[#1069cf]" data-node-id="529:14078">
        <p className="text-[13px] leading-[18px] font-semibold text-white">You're owed</p>
        <p className="text-[32px] leading-[38px] font-bold text-white">$3,892</p>
        <p className="text-[12px] leading-[16px] text-white/90">7 open invoices · 2 overdue</p>
        <div className="flex gap-2">
          <span className="px-[12px] py-[6px] text-[14px] leading-[20px]">Send reminders</span>
        </div>
      </div>
      <div className="flex flex-col gap-[4px] p-3 border rounded-[11px]" data-node-id="575:4638">
        <p className="text-[15px] leading-[20px] font-semibold text-[#b50012]">2 disputes · $2,322</p>
        <p style={{ fontSize: "13px", lineHeight: "18px" }}>Respond within 7 days to avoid auto-loss</p>
      </div>
    </div>
  );
}
