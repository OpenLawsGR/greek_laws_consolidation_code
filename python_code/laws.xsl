<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" version="1.0" encoding = "UTF-8" indent = "yes"
doctype-system = "httpQ//www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"/>
<xsl:strip-space elements="book part section chapter article paragraph mod" />

<xsl:template match="/">
	<html>
		<body>
			<h1 align = "center"> Νόμος <xsl:value-of select="law/@number"/> (ΦΕΚ <xsl:value-of select="law/@fek"/>/Τεύχος Α'/<xsl:value-of select="law/@year"/>) 
			</h1>
			<xsl:apply-templates/>
		</body>
	</html>
	
	</xsl:template>

	<xsl:template match="book">
		<xsl:apply-templates/>
	</xsl:template>

	<xsl:template match="part">
		<xsl:apply-templates/>
	</xsl:template>

	<xsl:template match="section">
		<xsl:apply-templates/>
	</xsl:template>

	<xsl:template match="chapter">
		<xsl:apply-templates/>
	</xsl:template>

	<xsl:template match="article">
		<xsl:text>&#xa;</xsl:text>
		<xsl:apply-templates select="header"/>
		<xsl:apply-templates select="title"/>

		<xsl:for-each select="paragraph">
			<xsl:choose>
				<xsl:when test="mod">
					<p style = "background-color:Crimson">
						<xsl:value-of select="mod/text()"/>
						<xsl:text>&#xa;</xsl:text>
					</p>
				</xsl:when>
				<xsl:otherwise>
					<p>
						<xsl:value-of select="text()"/>
						<xsl:text>&#xa;</xsl:text>
					</p>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:for-each>
		
	</xsl:template>


	<xsl:template match="header">
		<h4 align = "center" style="color:blue">
			<xsl:value-of select="text()"/>
		</h4>
		<xsl:text>&#xa;</xsl:text>
	</xsl:template>

	<xsl:template match="title">
		<h4 align = "center">
			<xsl:value-of select="text()"/>
		</h4>
		<xsl:text>&#xa;</xsl:text>
	</xsl:template>

</xsl:stylesheet>
