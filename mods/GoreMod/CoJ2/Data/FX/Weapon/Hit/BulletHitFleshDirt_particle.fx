ParticleDef()
{
	LifeTime()
	{
		keyf(0, 2)

	}

	Material("Flesh_particleMUL.mat", "Flesh_particleMUL.mat")
	Size()
	{
		randf(0, 5, 9)
		randf(1, 25, 45)
		randf(2, 46, 51)

	}

	Color()
	{
		keyv4(0,   1, 1, 1, 0.7)
		keyv4(0.5,   1, 1, 1, 0.4)
		keyv4(2,   1, 1, 1, 0)
	}

	GravityMul()
	{
		keyf(0, 0.5)
	}

	Rotation()
	{
		randf(0, 0, 360)
	}

	Drag()
	{
		keyf(0, 1)
	}
}
