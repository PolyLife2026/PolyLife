export default function BrandDivider({ compact = false }) {
  return (
    <span className={`brand-divider ${compact ? 'brand-divider--compact' : ''}`} aria-hidden="true">
      <span className="brand-divider__line" />
      <span className="brand-divider__dot" />
    </span>
  );
}
