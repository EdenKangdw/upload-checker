export default function Error ({errorMessage}: {errorMessage:string}) {
  return (
    <p className="text-[#D72323] my-6">{errorMessage}</p>
  );
};