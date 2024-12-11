export default function formatDate(
  dateString: string | Date,
  options: Intl.DateTimeFormatOptions = {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "short",
    year: "numeric",
  },
): string {
  let date: Date;
  if (typeof dateString === "string") {
    date = new Date(dateString);
  } else {
    date = dateString;
  }
  return new Intl.DateTimeFormat("default", options).format(date);
}
