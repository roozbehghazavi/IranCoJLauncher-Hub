ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.4)
	}

	GravityMul()
	{
		randf(0, 1.2, 1.6)
	}

	Drag()
	{
		randf(0, 0.5, 1)
	}

	Color()
	{
		keyv4(0, 0.55, 0.55, 0.55, 1)
		keyv4(0.17, 0.55, 0.55, 0.55, 0.86)
		keyv4(0.272, 0.55, 0.55, 0.55, 0.5)
		keyv4(0.84, 0.55, 0.55, 0.55, 0.12)
		keyv4(1.4, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		randf(0, 14, 22)
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
