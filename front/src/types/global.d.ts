declare module "*.png";
declare module "*.jpg";
declare module '*.gif';
declare module "*.webp";

declare module '*.svg' {
  import React = require('react');
  import { ReactElement, SVGProps } from 'react';
  export const ReactComponent: React.SFC<React.SVGProps<SVGSVGElement>>;
  const src: string;
  export default src;
}