ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1)
	}

	GravityMul()
	{
		randf(0, 1.3, 1.6)
	}

	Drag()
	{
		randf(0, 0.8, 1.2)
	}

	Color()
	{
		keyv4(0, 0.55, 0.55, 0.55, 1)
		keyv4(0.17, 0.55, 0.55, 0.55, 0.86)
		keyv4(0.272, 0.55, 0.55, 0.55, 0.5)
		keyv4(0.6, 0.55, 0.55, 0.55, 0.12)
		keyv4(1, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		randf(0, 9, 14)
	}

	Align("always")

	AspectRatio()
	{
		randf(0, 0.25, 0.35)
	}

	Material("IRN_BloodLine_particleBLEND.mat", "IRN_BloodLine_particleBLEND.mat")

	TexMultiRect(4, 1, 4)
	TexPlayMode("random_once", 1)
}
